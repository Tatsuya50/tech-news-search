from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class ArxivDailyDigest(Base):
    __tablename__ = "arxiv_daily_digests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    digest_date: Mapped[str] = mapped_column(String(10), unique=True)  # "2026-04-15"
    article_count: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
