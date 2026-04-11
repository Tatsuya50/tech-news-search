import json
from datetime import datetime

from sqlalchemy import DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class SearchHistory(Base):
    __tablename__ = "search_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    query: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    _retrieved_doc_ids: Mapped[str] = mapped_column("retrieved_doc_ids", Text, default="[]")
    searched_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    @property
    def retrieved_doc_ids(self) -> list[int]:
        return json.loads(self._retrieved_doc_ids)

    @retrieved_doc_ids.setter
    def retrieved_doc_ids(self, value: list[int]) -> None:
        self._retrieved_doc_ids = json.dumps(value)
