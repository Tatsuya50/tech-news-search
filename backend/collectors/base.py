from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ArticleData:
    source: str
    external_id: str
    title: str
    url: str
    published_at: datetime
    language: str
    summary: str | None = None
    body_text: str | None = None
    author: str | None = None
    tags: list[str] = field(default_factory=list)
    like_count: int = 0


class BaseCollector(ABC):
    source_name: str

    @abstractmethod
    async def collect(self) -> list[ArticleData]:
        """記事・論文を収集して返す"""
        ...
