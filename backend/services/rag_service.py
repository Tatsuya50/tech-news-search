"""RAGサービス: ChromaDB + OpenAI Embeddings + OpenAI Chat による実装"""

import os
import uuid
from datetime import datetime, timezone

import structlog
import tiktoken
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.models.article import Article
from backend.models.rag_document import RagDocument
from backend.models.search_history import SearchHistory
from backend.schemas.rag import RagDocumentResponse, RagSearchResponse, RagSourceItem

logger = structlog.get_logger()

CHUNK_SIZE = 512    # トークン数
CHUNK_OVERLAP = 64  # チャンク間オーバーラップ
COLLECTION_NAME = "tech_articles"


def _openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.openai_api_key)


def _get_chroma_collection():
    import chromadb
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _chunk_text(text: str) -> list[str]:
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + CHUNK_SIZE, len(tokens))
        chunks.append(enc.decode(tokens[start:end]))
        if end == len(tokens):
            break
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def _is_configured() -> bool:
    key = settings.openai_api_key
    return bool(key) and not key.startswith("sk-...")


async def _embed(texts: list[str]) -> list[list[float]]:
    """OpenAI text-embedding-3-small で埋め込みベクトルを生成する"""
    client = _openai_client()
    resp = await client.embeddings.create(
        model=settings.openai_embedding_model,
        input=texts,
    )
    return [item.embedding for item in resp.data]


async def index_article(session: AsyncSession, article_id: int) -> bool:
    """記事を ChromaDB に登録する"""
    article = await session.get(Article, article_id)
    if not article:
        return False

    if not _is_configured():
        logger.warning("OPENAI_API_KEY not configured, skipping embedding")
        article.is_indexed = True
        await session.commit()
        return True

    # 既存インデックスを削除してから再登録
    await remove_index(session, article_id)
    await session.refresh(article)

    source_text = "\n\n".join(filter(None, [article.title, article.summary, article.body_text]))
    if not source_text.strip():
        source_text = article.title

    chunks = _chunk_text(source_text)

    try:
        embeddings = await _embed(chunks)
        collection = _get_chroma_collection()

        rag_docs = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            doc_id = str(uuid.uuid4())
            collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "article_id": article_id,
                    "source": article.source,
                    "language": article.language,
                    "title": article.title,
                    "url": article.url,
                    "chunk_index": i,
                }],
            )
            rag_docs.append(RagDocument(
                article_id=article_id,
                chroma_doc_id=doc_id,
                chunk_index=i,
                chunk_text=chunk,
                indexed_at=datetime.now(timezone.utc),
            ))

        for doc in rag_docs:
            session.add(doc)
        article.is_indexed = True
        await session.commit()
        logger.info("Article indexed", article_id=article_id, chunks=len(chunks))
        return True

    except Exception as e:
        logger.error("RAG index failed", article_id=article_id, error=str(e))
        raise


async def remove_index(session: AsyncSession, article_id: int) -> bool:
    """ChromaDB から記事を削除する"""
    article = await session.get(Article, article_id)
    if not article:
        return False

    result = await session.scalars(
        select(RagDocument).where(RagDocument.article_id == article_id)
    )
    docs = list(result.all())

    if docs:
        try:
            collection = _get_chroma_collection()
            collection.delete(ids=[d.chroma_doc_id for d in docs])
        except Exception as e:
            logger.warning("ChromaDB delete error", error=str(e))
        for doc in docs:
            await session.delete(doc)

    article.is_indexed = False
    await session.commit()
    return True


async def search(
    session: AsyncSession,
    query: str,
    top_k: int = 5,
    filter_source: list[str] | None = None,
    filter_language: str | None = None,
) -> RagSearchResponse:
    """ベクトル検索 + OpenAI Chat による回答生成"""
    if not _is_configured():
        return RagSearchResponse(
            answer="OPENAI_API_KEY が設定されていません。.env ファイルに有効なキーを設定してください。",
            sources=[],
            searched_at=datetime.now(timezone.utc),
        )

    try:
        client = _openai_client()

        # クエリを埋め込みベクトルに変換
        query_resp = await client.embeddings.create(
            model=settings.openai_embedding_model,
            input=[query],
        )
        query_embedding = query_resp.data[0].embedding

        # ChromaDB でベクトル検索
        collection = _get_chroma_collection()
        where: dict = {}
        if filter_source:
            where["source"] = {"$in": filter_source}
        if filter_language:
            where["language"] = filter_language

        search_kwargs: dict = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k * 2, 20),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            search_kwargs["where"] = where

        results = collection.query(**search_kwargs)

        if not results["documents"] or not results["documents"][0]:
            return RagSearchResponse(
                answer="関連する記事が見つかりませんでした。重要マークをつけた記事が少ない可能性があります。",
                sources=[],
                searched_at=datetime.now(timezone.utc),
            )

        # 記事ごとに最もスコアの高いチャンクを選択
        seen: dict[int, dict] = {}
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            art_id = int(meta["article_id"])
            score = 1.0 - float(dist)
            if art_id not in seen or seen[art_id]["score"] < score:
                seen[art_id] = {"score": score, "doc": doc, "title": meta["title"], "url": meta["url"]}

        top_items = sorted(seen.items(), key=lambda x: x[1]["score"], reverse=True)[:top_k]

        # OpenAI Chat でコンテキストを組み立てて回答生成
        context = "\n\n---\n\n".join(
            f"[記事 {art_id}] {info['title']}\n{info['doc']}"
            for art_id, info in top_items
        )

        completion = await client.chat.completions.create(
            model=settings.openai_model,
            max_tokens=1024,
            messages=[
                {
                    "role": "system",
                    "content": "あなたは技術記事・論文の内容を参考に質問に答えるアシスタントです。回答は日本語で行い、参照した記事を [記事 X] の形式で引用してください。",
                },
                {
                    "role": "user",
                    "content": f"## 参考文献\n{context}\n\n## 質問\n{query}",
                },
            ],
        )
        answer = completion.choices[0].message.content or ""

        sources = [
            RagSourceItem(
                article_id=art_id,
                title=info["title"],
                url=info["url"],
                relevance_score=round(info["score"], 4),
            )
            for art_id, info in top_items
        ]

        # 検索履歴を保存
        history = SearchHistory(
            query=query,
            answer=answer,
            searched_at=datetime.now(timezone.utc),
        )
        history.retrieved_doc_ids = [art_id for art_id, _ in top_items]
        session.add(history)
        await session.commit()

        return RagSearchResponse(
            answer=answer,
            sources=sources,
            searched_at=datetime.now(timezone.utc),
        )

    except Exception as e:
        logger.error("RAG search failed", error=str(e))
        raise


async def get_documents(session: AsyncSession) -> list[RagDocumentResponse]:
    result = await session.scalars(
        select(RagDocument).order_by(RagDocument.indexed_at.desc()).limit(100)
    )
    return [RagDocumentResponse.model_validate(d) for d in result.all()]


async def get_history(session: AsyncSession, limit: int = 20) -> list[SearchHistory]:
    result = await session.scalars(
        select(SearchHistory).order_by(SearchHistory.searched_at.desc()).limit(limit)
    )
    return list(result.all())
