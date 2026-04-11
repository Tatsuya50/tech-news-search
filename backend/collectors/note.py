import hashlib
import structlog
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser

from backend.collectors.base import ArticleData, BaseCollector

logger = structlog.get_logger()

NOTE_HASHTAGS = ["LLM", "生成AI", "RAG", "機械学習", "データエンジニアリング"]


class NoteCollector(BaseCollector):
    source_name = "note"

    async def collect(self) -> list[ArticleData]:
        articles: list[ArticleData] = []
        seen_ids: set[str] = set()

        for hashtag in NOTE_HASHTAGS:
            try:
                feed = feedparser.parse(f"https://note.com/hashtag/{hashtag}?rss=1")
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
                            source="note",
                            external_id=external_id,
                            title=entry.get("title", ""),
                            url=url,
                            published_at=published,
                            language="ja",
                            summary=entry.get("summary", "")[:500] or None,
                            author=entry.get("author"),
                            tags=[hashtag],
                        )
                    )
            except Exception as e:
                logger.error("Note collection error", hashtag=hashtag, error=str(e))

        logger.info("Note collected", count=len(articles))
        return articles
