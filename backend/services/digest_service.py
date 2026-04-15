from datetime import date, datetime, timezone  # timezone は generated_at で使用

import structlog
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.models.article import Article
from backend.models.arxiv_daily_digest import ArxivDailyDigest
from backend.schemas.digest import ArxivArticleDigest, ArxivDailyDigestResponse

logger = structlog.get_logger()


def _openai_client() -> AsyncOpenAI | None:
    if not settings.openai_api_key:
        return None
    return AsyncOpenAI(api_key=settings.openai_api_key)


async def get_today_arxiv_digest(session: AsyncSession) -> ArxivDailyDigestResponse:
    # SQLite は timezone-naive な文字列で保存するため naive datetime で比較する
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_str = date.today().isoformat()

    result = await session.scalars(
        select(Article)
        .where(Article.source == "arxiv")
        .where(Article.collected_at >= today_start)
        .order_by(Article.published_at.desc())
    )
    articles = list(result.all())

    client = _openai_client()
    if client and articles:
        await _generate_missing_summaries(session, articles, client)

    overall_digest = await _get_or_create_overall_digest(session, articles, today_str, client)

    return ArxivDailyDigestResponse(
        date=today_str,
        articles=[ArxivArticleDigest.model_validate(a) for a in articles],
        total_count=len(articles),
        overall_digest=overall_digest,
    )


async def _generate_missing_summaries(
    session: AsyncSession, articles: list[Article], client: AsyncOpenAI
) -> None:
    for article in articles:
        if article.summary_ja is not None:
            continue
        source_text = article.summary or article.title
        try:
            completion = await client.chat.completions.create(
                model=settings.openai_model,
                max_tokens=300,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "あなたは学術論文の内容を日本語で分かりやすく要約するアシスタントです。"
                            "与えられた論文のアブストラクトを日本語で3文程度に要約してください。"
                            "専門用語は適切に訳し、研究の目的・手法・主な結果を含めてください。"
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"論文タイトル: {article.title}\n\nアブストラクト: {source_text}",
                    },
                ],
            )
            article.summary_ja = completion.choices[0].message.content or ""
            await session.commit()
        except Exception as e:
            logger.warning("summary_ja generation failed", article_id=article.id, error=str(e))


async def _get_or_create_overall_digest(
    session: AsyncSession,
    articles: list[Article],
    today_str: str,
    client: AsyncOpenAI | None,
) -> str | None:
    if not articles:
        return None

    existing = await session.scalar(
        select(ArxivDailyDigest).where(ArxivDailyDigest.digest_date == today_str)
    )
    if existing:
        return existing.content

    if not client:
        return None

    titles_block = "\n".join(
        f"{i + 1}. {a.title}" for i, a in enumerate(articles[:50])
    )
    try:
        completion = await client.chat.completions.create(
            model=settings.openai_model,
            max_tokens=800,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "あなたはarXivの最新論文動向を分析する研究アシスタントです。"
                        "今日公開された論文リストを見て、全体的な研究トレンドや注目すべきテーマを"
                        "日本語で包括的にまとめてください。"
                    ),
                },
                {
                    "role": "user",
                    "content": f"今日のarXiv論文リスト（{len(articles)}件）:\n\n{titles_block}",
                },
            ],
        )
        content = completion.choices[0].message.content or ""
        digest_record = ArxivDailyDigest(
            digest_date=today_str,
            article_count=len(articles),
            content=content,
            generated_at=datetime.now(timezone.utc),
        )
        session.add(digest_record)
        await session.commit()
        return content
    except Exception as e:
        logger.error("overall digest generation failed", error=str(e))
        return None
