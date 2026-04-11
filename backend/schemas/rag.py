from datetime import datetime

from pydantic import BaseModel


class RagSearchRequest(BaseModel):
    query: str
    top_k: int = 5
    filter_source: list[str] | None = None
    filter_language: str | None = None


class RagSourceItem(BaseModel):
    article_id: int
    title: str
    url: str
    relevance_score: float


class RagSearchResponse(BaseModel):
    answer: str
    sources: list[RagSourceItem]
    searched_at: datetime


class RagDocumentResponse(BaseModel):
    id: int
    article_id: int
    chunk_index: int
    chunk_text: str
    indexed_at: datetime

    class Config:
        from_attributes = True


class SearchHistoryResponse(BaseModel):
    id: int
    query: str
    answer: str
    searched_at: datetime

    class Config:
        from_attributes = True
