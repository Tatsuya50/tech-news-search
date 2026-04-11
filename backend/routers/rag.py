from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.schemas.rag import (
    RagDocumentResponse,
    RagSearchRequest,
    RagSearchResponse,
    SearchHistoryResponse,
)
from backend.services import rag_service

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/index/{article_id}")
async def index_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    ok = await rag_service.index_article(db, article_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "Indexed", "article_id": article_id}


@router.delete("/index/{article_id}")
async def remove_index(
    article_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    ok = await rag_service.remove_index(db, article_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "Removed from index", "article_id": article_id}


@router.post("/search", response_model=RagSearchResponse)
async def search(
    req: RagSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> RagSearchResponse:
    return await rag_service.search(
        db,
        query=req.query,
        top_k=req.top_k,
        filter_source=req.filter_source,
        filter_language=req.filter_language,
    )


@router.get("/documents", response_model=list[RagDocumentResponse])
async def get_documents(
    db: AsyncSession = Depends(get_db),
) -> list[RagDocumentResponse]:
    return await rag_service.get_documents(db)


@router.get("/history", response_model=list[SearchHistoryResponse])
async def get_history(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> list[SearchHistoryResponse]:
    histories = await rag_service.get_history(db, limit=limit)
    return [SearchHistoryResponse.model_validate(h) for h in histories]
