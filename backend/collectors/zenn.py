import hashlib
import structlog
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser

from backend.collectors.base import ArticleData, BaseCollector

logger = structlog.get_logger()

ZENN_TOPICS = ["llm", "rag", "機械学習", "データエンジニアリング", "mlops", "生成ai"]


class ZennCollector(BaseCollector):
    source_name = "zenn"

    async def collect(self) -> list[ArticleData]:
        articles: list[ArticleData] = []
        seen_ids: set[str] = set()

        for topic in ZENN_TOPICS:
            try:
                feed = feedparser.parse(f"https://zenn.dev/topics/{topic}/feed")
                for entry in feed.entries:
                    url = entry.get("link", "")
                    external_id = hashlib.md5(url.encode()).hexdigest()
                    if external_id in seen_ids:
                        continue
                    seen_ids.add(external_id)

                    try:
                        published = parsedate_to_datetime(entry.get("published", ""))
                        published = published.replace(tzinfo=timezone.utc)
                    except Exception:
                        published = datetime.now(timezone.utc)

                    articles.append(
                        ArticleData(
                            source="zenn",
                            external_id=external_id,
                            title=entry.get("title", ""),
                            url=url,
                            published_at=published,
                            language="ja",
                            summary=entry.get("summary", "")[:500] or None,
                            author=entry.get("author"),
                            tags=[topic],
                        )
                    )
            except Exception as e:
                logger.error("Zenn collection error", topic=topic, error=str(e))

        logger.info("Zenn collected", count=len(articles))
        return articles
