import json
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base

if TYPE_CHECKING:
    from backend.models.rag_document import RagDocument


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(20))        # qiita | zenn | note | arxiv
    external_id: Mapped[str] = mapped_column(String(255))  # 各ソースでのID
    title: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    _tags: Mapped[str] = mapped_column("tags", Text, default="[]")
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False)
    is_indexed: Mapped[bool] = mapped_column(Boolean, default=False)
    language: Mapped[str] = mapped_column(String(5))       # ja | en
    summary_ja: Mapped[str | None] = mapped_column(Text, nullable=True)

    rag_documents: Mapped[list["RagDocument"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )

    @property
    def tags(self) -> list[str]:
        return json.loads(self._tags)

    @tags.setter
    def tags(self, value: list[str]) -> None:
        self._tags = json.dumps(value, ensure_ascii=False)
