import asyncio
import structlog
from datetime import timezone

import arxiv

from backend.collectors.base import ArticleData, BaseCollector

logger = structlog.get_logger()

ARXIV_CATEGORIES = ["cs.AI", "cs.LG", "cs.DB", "cs.IR"]
MAX_RESULTS_PER_CATEGORY = 5


class ArxivCollector(BaseCollector):
    source_name = "arxiv"

    def _collect_sync(self) -> list[ArticleData]:
        articles: list[ArticleData] = []
        seen_ids: set[str] = set()

        query = " OR ".join(f"cat:{cat}" for cat in ARXIV_CATEGORIES)
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=MAX_RESULTS_PER_CATEGORY * len(ARXIV_CATEGORIES),
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        for result in client.results(search):
            external_id = result.entry_id.split("/")[-1]
            if external_id in seen_ids:
                continue
            seen_ids.add(external_id)

            published = result.published
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)

            articles.append(
                ArticleData(
                    source="arxiv",
                    external_id=external_id,
                    title=result.title,
                    url=result.entry_id,
                    published_at=published,
                    language="en",
                    summary=result.summary[:1000],
                    author=", ".join(a.name for a in result.authors[:3]),
                    tags=[c for c in result.categories if c in ARXIV_CATEGORIES],
                )
            )
        return articles

    async def collect(self) -> list[ArticleData]:
        try:
            articles = await asyncio.to_thread(self._collect_sync)
        except Exception as e:
            logger.error("arXiv collection error", error=str(e))
            articles = []

        logger.info("arXiv collected", count=len(articles))
        return articles
