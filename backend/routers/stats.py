from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.article import Article
from backend.schemas.stats import SourceCount, StatsOverviewResponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=StatsOverviewResponse)
async def overview(db: AsyncSession = Depends(get_db)) -> StatsOverviewResponse:
    total = await db.scalar(select(func.count(Article.id))) or 0
    important = await db.scalar(
        select(func.count(Article.id)).where(Article.is_important == True)  # noqa: E712
    ) or 0
    indexed = await db.scalar(
        select(func.count(Article.id)).where(Article.is_indexed == True)  # noqa: E712
    ) or 0

    rows = await db.execute(
        select(Article.source, func.count(Article.id)).group_by(Article.source)
    )
    by_source = [SourceCount(source=row[0], count=row[1]) for row in rows.all()]

    return StatsOverviewResponse(
        total_articles=total,
        important_articles=important,
        indexed_articles=indexed,
        by_source=by_source,
    )
