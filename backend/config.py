from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # Qiita
    qiita_access_token: str = ""

    # データベース
    database_url: str = "sqlite+aiosqlite:///./data/app.db"

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma"

    # スケジューラ
    collection_interval_minutes: int = 60
    arxiv_collection_hour: int = 6

    # アプリ
    app_env: str = "development"
    frontend_origin: str = "http://localhost:5173"


settings = Settings()
