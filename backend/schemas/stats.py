from pydantic import BaseModel


class SourceCount(BaseModel):
    source: str
    count: int


class StatsOverviewResponse(BaseModel):
    total_articles: int
    important_articles: int
    indexed_articles: int
    by_source: list[SourceCount]
