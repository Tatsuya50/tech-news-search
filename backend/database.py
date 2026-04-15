import os
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.config import settings

# data/ ディレクトリを自動作成
os.makedirs("data", exist_ok=True)

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # 既存DB向けマイグレーション: summary_ja カラムがなければ追加
        try:
            await conn.execute(text("ALTER TABLE articles ADD COLUMN summary_ja TEXT"))
        except Exception:
            pass  # カラムが既に存在する場合は無視
