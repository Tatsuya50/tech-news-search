import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.routers import articles, collector, rag, stats
from backend.services.collector_service import CollectorService

logger = structlog.get_logger()

app = FastAPI(title="Tech News Search API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router, prefix="/api/v1")
app.include_router(collector.router, prefix="/api/v1")
app.include_router(rag.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")

_collector_service: CollectorService | None = None


@app.on_event("startup")
async def startup() -> None:
    await init_db()
    global _collector_service
    _collector_service = CollectorService()
    await _collector_service.start()
    logger.info("App started")


@app.on_event("shutdown")
async def shutdown() -> None:
    if _collector_service:
        await _collector_service.stop()
    logger.info("App shutdown")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
