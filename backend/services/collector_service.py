from datetime import datetime, timezone

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.collectors.arxiv import ArxivCollector
from backend.collectors.base import ArticleData, BaseCollector
from backend.collectors.note import NoteCollector
from backend.collectors.qiita import QiitaCollector
from backend.collectors.zenn import ZennCollector
from backend.config import settings
from backend.database import AsyncSessionLocal
from backend.models.article import Article
from backend.models.collection_log import CollectionLog

logger = structlog.get_logger()

COLLECTORS: dict[str, type[BaseCollector]] = {
    "qiita": QiitaCollector,
    "zenn": ZennCollector,
    "note": NoteCollector,
    "arxiv": ArxivCollector,
}


async def _save_articles(session: AsyncSession, articles: list[ArticleData]) -> tuple[int, int]:
    found = len(articles)
    new_count = 0
    for data in articles:
        existing = await session.scalar(
            select(Article).where(
                Article.source == data.source,
                Article.external_id == data.external_id,
            )
        )
        if existing:
            continue
        article = Article(
            source=data.source,
            external_id=data.external_id,
            title=data.title,
            url=data.url,
            published_at=data.published_at,
            language=data.language,
            summary=data.summary,
            body_text=data.body_text,
            author=data.author,
            like_count=data.like_count,
            collected_at=datetime.now(timezone.utc),
        )
        article.tags = data.tags
        session.add(article)
        new_count += 1
    await session.commit()
    return found, new_count


async def run_collector(source: str) -> CollectionLog:
    collector_cls = COLLECTORS.get(source)
    if not collector_cls:
        raise ValueError(f"Unknown source: {source}")

    async with AsyncSessionLocal() as session:
        log = CollectionLog(source=source, started_at=datetime.now(timezone.utc))
        session.add(log)
        await session.commit()
        await session.refresh(log)
        log_id = log.id

    try:
        collector = collector_cls()
        articles = await collector.collect()

        async with AsyncSessionLocal() as session:
            found, new_count = await _save_articles(session, articles)
            log = await session.get(CollectionLog, log_id)
            log.finished_at = datetime.now(timezone.utc)
            log.articles_found = found
            log.articles_new = new_count
            log.status = "success"
            await session.commit()
            await session.refresh(log)
            return log
    except Exception as e:
        logger.error("Collector failed", source=source, error=str(e))
        async with AsyncSessionLocal() as session:
            log = await session.get(CollectionLog, log_id)
            log.finished_at = datetime.now(timezone.utc)
            log.status = "failed"
            log.error_message = str(e)
            await session.commit()
            await session.refresh(log)
            return log


class CollectorService:
    def __init__(self) -> None:
        self._scheduler = AsyncIOScheduler()

    async def start(self) -> None:
        # 毎時: Qiita / Zenn / Note
        for source in ["qiita", "zenn", "note"]:
            self._scheduler.add_job(
                run_collector,
                "interval",
                minutes=settings.collection_interval_minutes,
                args=[source],
                id=f"collect_{source}",
                replace_existing=True,
            )
        # 毎日 指定時刻: arXiv
        self._scheduler.add_job(
            run_collector,
            "cron",
            hour=settings.arxiv_collection_hour,
            minute=0,
            args=["arxiv"],
            id="collect_arxiv",
            replace_existing=True,
        )
        self._scheduler.start()
        logger.info("Scheduler started")

    async def stop(self) -> None:
        self._scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
