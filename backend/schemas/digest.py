from datetime import datetime

from pydantic import BaseModel


class ArxivArticleDigest(BaseModel):
    id: int
    title: str
    url: str
    author: str | None
    published_at: datetime
    summary: str | None
    summary_ja: str | None
    tags: list[str]
    is_important: bool

    model_config = {"from_attributes": True}


class ArxivDailyDigestResponse(BaseModel):
    date: str
    articles: list[ArxivArticleDigest]
    total_count: int
    overall_digest: str | None
