from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    title: str
    url: str
    summary: str | None
    author: str | None
    published_at: datetime
    collected_at: datetime
    tags: list[str]
    like_count: int
    is_important: bool
    is_indexed: bool
    language: str


class ArticleListResponse(BaseModel):
    items: list[ArticleResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
