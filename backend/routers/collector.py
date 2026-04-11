from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.collection_log import CollectionLog
from backend.schemas.collector import CollectionLogResponse, CollectorRunResponse
from backend.services.collector_service import COLLECTORS, run_collector

router = APIRouter(prefix="/collector", tags=["collector"])


@router.post("/run", response_model=CollectorRunResponse)
async def run_all() -> CollectorRunResponse:
    import asyncio
    sources = list(COLLECTORS.keys())
    asyncio.create_task(asyncio.gather(*[run_collector(s) for s in sources]))
    return CollectorRunResponse(message="Collection started", sources=sources)


@router.post("/run/{source}", response_model=CollectionLogResponse)
async def run_source(source: str) -> CollectionLogResponse:
    if source not in COLLECTORS:
        raise HTTPException(status_code=400, detail=f"Unknown source: {source}")
    log = await run_collector(source)
    return CollectionLogResponse.model_validate(log)


@router.get("/logs", response_model=list[CollectionLogResponse])
async def get_logs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[CollectionLogResponse]:
    result = await db.scalars(
        select(CollectionLog).order_by(CollectionLog.started_at.desc()).limit(limit)
    )
    return [CollectionLogResponse.model_validate(log) for log in result.all()]
