import math

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.article import Article
from backend.schemas.article import ArticleListResponse, ArticleResponse


async def get_articles(
    session: AsyncSession,
    sources: list[str] | None = None,
    language: str | None = None,
    tags: list[str] | None = None,
    is_important: bool | None = None,
    keyword: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> ArticleListResponse:
    q = select(Article)
    if sources:
        q = q.where(Article.source.in_(sources))
    if language:
        q = q.where(Article.language == language)
    if is_important is not None:
        q = q.where(Article.is_important == is_important)
    if keyword:
        like = f"%{keyword}%"
        q = q.where(or_(Article.title.ilike(like), Article.summary.ilike(like)))

    count_q = select(func.count()).select_from(q.subquery())
    total = await session.scalar(count_q) or 0

    q = q.order_by(Article.published_at.desc())
    q = q.offset((page - 1) * per_page).limit(per_page)
    result = await session.scalars(q)
    items = list(result.all())

    # タグフィルタはPython側で（JSON列のためDB側フィルタが煩雑）
    if tags:
        items = [a for a in items if any(t in a.tags for t in tags)]

    return ArticleListResponse(
        items=[ArticleResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=math.ceil(total / per_page),
    )


async def toggle_important(session: AsyncSession, article_id: int) -> Article | None:
    article = await session.get(Article, article_id)
    if not article:
        return None
    article.is_important = not article.is_important
    await session.commit()
    await session.refresh(article)
    return article
