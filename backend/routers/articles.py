from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.schemas.article import ArticleListResponse, ArticleResponse
from backend.services import article_service, rag_service

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=ArticleListResponse)
async def list_articles(
    source: list[str] | None = Query(None),
    language: str | None = Query(None),
    tags: list[str] | None = Query(None),
    is_important: bool | None = Query(None),
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> ArticleListResponse:
    return await article_service.get_articles(
        db,
        sources=source,
        language=language,
        tags=tags,
        is_important=is_important,
        keyword=keyword,
        page=page,
        per_page=per_page,
    )


@router.patch("/{article_id}/important", response_model=ArticleResponse)
async def toggle_important(
    article_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> ArticleResponse:
    article = await article_service.toggle_important(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # 重要マーク ON → バックグラウンドでRAG登録
    # 重要マーク OFF → バックグラウンドでRAG削除
    if article.is_important:
        background_tasks.add_task(_index_in_background, article_id)
    else:
        background_tasks.add_task(_remove_index_in_background, article_id)

    return ArticleResponse.model_validate(article)


async def _index_in_background(article_id: int) -> None:
    from backend.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        await rag_service.index_article(session, article_id)


async def _remove_index_in_background(article_id: int) -> None:
    from backend.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        await rag_service.remove_index(session, article_id)
