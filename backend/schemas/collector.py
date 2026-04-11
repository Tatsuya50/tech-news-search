from datetime import datetime

from pydantic import BaseModel


class CollectionLogResponse(BaseModel):
    id: int
    source: str
    started_at: datetime
    finished_at: datetime | None
    articles_found: int
    articles_new: int
    status: str
    error_message: str | None

    class Config:
        from_attributes = True


class CollectorRunResponse(BaseModel):
    message: str
    sources: list[str]
