# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

- Python仮想環境は `uv` を使用する（`uv sync` で依存関係インストール、`uv run` でコマンド実行）

## Communication

- 思考・推論は英語で行う
- ユーザとのコミュニケーション（実装計画・説明・質問・回答）はすべて日本語で行う

## Commands

### バックエンド
```bash
# 依存関係インストール
uv sync

# 開発サーバ起動
uv run uvicorn backend.main:app --reload

# テスト実行
uv run pytest

# 特定テスト
uv run pytest backend/tests/test_collectors.py -v

# Lint
uv run ruff check backend/
uv run ruff format backend/
```

### フロントエンド
```bash
cd frontend

# 依存関係インストール
npm install

# 開発サーバ起動（バックエンドと同時に起動すること）
npm run dev

# ビルド
npm run build
```

### 手動収集・動作確認
```bash
# 全ソース収集トリガー
curl -X POST http://localhost:8000/api/v1/collector/run

# 特定ソース収集（qiita / zenn / note / arxiv）
curl -X POST http://localhost:8000/api/v1/collector/run/zenn

# 収集ログ確認
curl http://localhost:8000/api/v1/collector/logs

# 統計確認
curl http://localhost:8000/api/v1/stats/overview
```

## Architecture

### ディレクトリ構成
```
tech_news_search/
├── backend/
│   ├── main.py              # FastAPI エントリポイント・ライフサイクル管理
│   ├── config.py            # pydantic-settings による設定（.env 読み込み）
│   ├── database.py          # SQLAlchemy async エンジン・セッション・Base
│   ├── models/              # SQLAlchemy ORM モデル
│   ├── schemas/             # Pydantic I/O スキーマ
│   ├── routers/             # FastAPI ルータ（articles / collector / rag / stats）
│   ├── services/            # ビジネスロジック
│   │   ├── article_service.py   # 記事CRUD・重要マークトグル
│   │   ├── collector_service.py # APScheduler管理・記事保存処理
│   │   └── rag_service.py       # RAG操作（Phase 2で本実装）
│   └── collectors/          # データ収集モジュール
│       ├── base.py          # BaseCollector 抽象クラス・ArticleData dataclass
│       ├── qiita.py         # Qiita API v2
│       ├── zenn.py          # Zenn RSS (feedparser)
│       ├── note.py          # Note RSS (feedparser)
│       └── arxiv.py         # arXiv 公式クライアント
├── frontend/
│   └── src/
│       ├── api/client.ts    # axios ベースの API クライアント・型定義
│       ├── stores/articles.ts # Pinia ストア（記事一覧・フィルタ・重要マーク）
│       ├── components/      # ArticleCard / SourceFilter
│       └── views/           # HomeView / ImportantView / SearchView
└── data/                    # SQLite・ChromaDB 永続化（gitignore済み）
```

### 主要な設計ポイント
- **コレクター**: `BaseCollector` を継承し `collect() -> list[ArticleData]` を実装する。重複防止は `(source, external_id)` の組み合わせで行う
- **スケジューラ**: `CollectorService` が APScheduler を管理。起動時に `main.py` の `startup` イベントで開始される
- **重要マーク**: `PATCH /api/v1/articles/{id}/important` でトグル。Phase 2ではここでRAGインデックスも自動実行予定
- **RAG**: `rag_service.py` はPhase 1ではスタブ実装。Phase 2でChromaDB + Voyage AI + Claude APIを本実装する
- **DB**: `database.py` の `init_db()` が起動時にテーブルを自動作成（Alembicなし、シンプル構成）

### 環境変数（.env）
```
ANTHROPIC_API_KEY      # Claude API（Phase 2 RAG用）
VOYAGE_API_KEY         # Voyage AI 埋め込み（Phase 2 RAG用）
QIITA_ACCESS_TOKEN     # Qiita API認証（未設定時は収集スキップ）
DATABASE_URL           # デフォルト: sqlite+aiosqlite:///./data/app.db
CHROMA_PERSIST_DIR     # デフォルト: ./data/chroma
COLLECTION_INTERVAL_MINUTES  # デフォルト: 60
ARXIV_COLLECTION_HOUR  # デフォルト: 6 (JST)
FRONTEND_ORIGIN        # デフォルト: http://localhost:5173
```
