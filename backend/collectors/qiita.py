import structlog
from datetime import datetime, timezone

import httpx

from backend.collectors.base import ArticleData, BaseCollector
from backend.config import settings

logger = structlog.get_logger()

QIITA_QUERIES = ["機械学習", "LLM", "RAG", "生成AI", "データエンジニアリング", "MLOps"]
QIITA_API_BASE = "https://qiita.com/api/v2"


class QiitaCollector(BaseCollector):
    source_name = "qiita"

    async def collect(self) -> list[ArticleData]:
        if not settings.qiita_access_token:
            logger.warning("QIITA_ACCESS_TOKEN not set, skipping Qiita collection")
            return []

        headers = {"Authorization": f"Bearer {settings.qiita_access_token}"}
        articles: list[ArticleData] = []
        seen_ids: set[str] = set()

        async with httpx.AsyncClient(timeout=30) as client:
            for query in QIITA_QUERIES:
                try:
                    resp = await client.get(
                        f"{QIITA_API_BASE}/items",
                        params={"query": f"tag:{query}", "per_page": 20, "sort": "created"},
                        headers=headers,
                    )
                    resp.raise_for_status()
                    for item in resp.json():
                        if item["id"] in seen_ids:
                            continue
                        seen_ids.add(item["id"])
                        published = datetime.fromisoformat(
                            item["created_at"].replace("Z", "+00:00")
                        ).replace(tzinfo=timezone.utc)
                        articles.append(
                            ArticleData(
                                source="qiita",
                                external_id=item["id"],
                                title=item["title"],
                                url=item["url"],
                                published_at=published,
                                language="ja",
                                summary=item.get("body", "")[:500] if item.get("body") else None,
                                author=item.get("user", {}).get("id"),
                                tags=[t["name"] for t in item.get("tags", [])],
                                like_count=item.get("likes_count", 0),
                            )
                        )
                except Exception as e:
                    logger.error("Qiita collection error", query=query, error=str(e))

        logger.info("Qiita collected", count=len(articles))
        return articles
