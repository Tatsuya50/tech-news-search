from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.schemas.digest import ArxivDailyDigestResponse
from backend.services import digest_service

router = APIRouter(prefix="/digest", tags=["digest"])


@router.get("/arxiv/today", response_model=ArxivDailyDigestResponse)
async def get_arxiv_today_digest(
    db: AsyncSession = Depends(get_db),
) -> ArxivDailyDigestResponse:
    """
    今日収集されたarXiv論文の一覧と日本語要約、および全体ダイジェストを返す。
    summary_ja 未生成の論文は初回呼び出し時に生成してDBにキャッシュする。
    """
    return await digest_service.get_today_arxiv_digest(db)
