<template>
  <div class="digest-wrap">
    <!-- ヘッダー -->
    <div class="page-heading">
      <span class="page-title">◈ arXiv DIGEST</span>
      <span v-if="data" class="digest-date-badge">{{ data.date }}</span>
      <span class="page-count">{{ data?.total_count ?? 0 }} 件</span>
    </div>

    <!-- ローディング -->
    <div v-if="loading" class="loading-state">
      <div class="spinner" />
      <p class="loading-hint">日本語要約を生成中です（初回のみ時間がかかります）</p>
    </div>

    <template v-else-if="data">
      <!-- OpenAI未設定の案内 -->
      <div v-if="!data.overall_digest && data.total_count > 0" class="info-bar">
        ◎ OPENAI_API_KEY が未設定のため日本語要約は生成されません。.env に設定後、バックエンドを再起動してください。
      </div>

      <!-- 全体ダイジェストブロック -->
      <div v-if="data.overall_digest" class="overall-block">
        <div class="overall-header">
          <span class="overall-label">◈ OVERALL SIGNAL</span>
          <span class="overall-meta">{{ data.total_count }}件の論文より生成</span>
        </div>
        <div class="overall-body">{{ data.overall_digest }}</div>
      </div>

      <!-- 論文一覧 -->
      <div class="section-label-row">PAPERS TODAY</div>

      <div v-if="data.articles.length > 0" class="digest-list">
        <div v-for="article in data.articles" :key="article.id" class="dcard">
          <!-- カードヘッダー -->
          <div class="dcard-header">
            <span class="source-badge">ARXIV</span>
            <span class="dcard-meta">
              {{ article.author ?? '—' }} · {{ formatDate(article.published_at) }}
            </span>
          </div>

          <!-- タイトル -->
          <a :href="article.url" target="_blank" rel="noopener" class="dcard-title">
            {{ article.title }}
          </a>

          <!-- 日本語要約 -->
          <p v-if="article.summary_ja" class="dcard-summary-ja">{{ article.summary_ja }}</p>
          <p v-else-if="!data.overall_digest" class="dcard-no-summary">要約未生成</p>

          <!-- 英語 abstract（折りたたみ） -->
          <details v-if="article.summary" class="dcard-abstract">
            <summary class="dcard-abstract-toggle">Abstract (EN)</summary>
            <p class="dcard-abstract-body">{{ article.summary }}</p>
          </details>

          <!-- タグ -->
          <div v-if="article.tags.length" class="dcard-tags">
            <span v-for="tag in article.tags.slice(0, 5)" :key="tag" class="tag">#{{ tag }}</span>
          </div>
        </div>
      </div>

      <!-- 論文なし -->
      <div v-else class="empty-state">
        <div class="empty-icon">◈</div>
        <div class="empty-text">TODAY'S ARXIV PAPERS NOT COLLECTED YET — CLICK ↺ 収集 TO FETCH</div>
      </div>
    </template>

    <!-- エラー -->
    <div v-if="error" class="error-bar">
      <span>{{ error }}</span>
      <button class="error-close" @click="error = null">✕</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { digestApi, type ArxivDailyDigestResponse } from '@/api/client'

const loading = ref(false)
const error = ref<string | null>(null)
const data = ref<ArxivDailyDigestResponse | null>(null)

async function fetchDigest() {
  loading.value = true
  error.value = null
  try {
    const resp = await digestApi.getArxivToday()
    data.value = resp.data
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'データの取得に失敗しました'
  } finally {
    loading.value = false
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('ja-JP', {
    month: 'short',
    day: 'numeric',
  })
}

onMounted(fetchDigest)
</script>

<style scoped>
.digest-wrap {
  max-width: 820px;
  margin: 0 auto;
}

/* ── ヘッダー ── */
.digest-date-badge {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--arxiv);
  border: 1px solid var(--arxiv);
  border-radius: 100px;
  padding: 0.15em 0.65em;
  background: rgba(100, 200, 255, 0.06);
}

/* ── ローディングヒント ── */
.loading-hint {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--muted);
  margin-top: 0.75rem;
  text-align: center;
}

/* ── 全体ダイジェストブロック ── */
.overall-block {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 1.75rem;
  animation: fadeUp 0.3s ease;
}

.overall-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 1rem;
  border-bottom: 1px solid var(--border);
  background: var(--accent-dim);
}

.overall-label {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
}

.overall-meta {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--muted);
}

.overall-body {
  padding: 1.1rem 1.25rem;
  font-size: 0.88rem;
  line-height: 1.8;
  color: var(--text);
  white-space: pre-wrap;
}

/* ── セクションラベル ── */
.section-label-row {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  letter-spacing: 0.12em;
  color: var(--muted);
  text-transform: uppercase;
  margin-bottom: 0.75rem;
}

/* ── 論文リスト ── */
.digest-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* ── 論文カード ── */
.dcard {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem 1.2rem;
  transition: border-color var(--t);
}

.dcard:hover {
  border-color: var(--arxiv);
}

.dcard-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.5rem;
}

.source-badge {
  font-family: var(--font-mono);
  font-size: 0.55rem;
  letter-spacing: 0.08em;
  padding: 0.2em 0.55em;
  border-radius: 100px;
  background: rgba(100, 200, 255, 0.12);
  color: var(--arxiv);
  border: 1px solid rgba(100, 200, 255, 0.3);
}

.dcard-meta {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--muted);
}

.dcard-title {
  display: block;
  font-family: var(--font-title);
  font-style: italic;
  font-size: 1rem;
  color: var(--text);
  text-decoration: none;
  margin-bottom: 0.65rem;
  line-height: 1.4;
  transition: color var(--t);
}

.dcard-title:hover {
  color: var(--arxiv);
}

.dcard-summary-ja {
  font-size: 0.875rem;
  line-height: 1.8;
  color: var(--text);
  margin: 0 0 0.75rem;
}

.dcard-no-summary {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--muted);
  margin: 0 0 0.5rem;
}

/* ── Abstract 折りたたみ ── */
.dcard-abstract {
  margin-top: 0.5rem;
}

.dcard-abstract-toggle {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--muted);
  cursor: pointer;
  list-style: none;
  user-select: none;
}

.dcard-abstract-toggle:hover {
  color: var(--text);
}

.dcard-abstract-toggle::marker,
.dcard-abstract-toggle::-webkit-details-marker {
  display: none;
}

.dcard-abstract-toggle::before {
  content: '▶ ';
}

details[open] .dcard-abstract-toggle::before {
  content: '▼ ';
}

.dcard-abstract-body {
  font-size: 0.8rem;
  line-height: 1.7;
  color: var(--muted);
  margin-top: 0.4rem;
  padding: 0.5rem 0.75rem;
  border-left: 2px solid var(--border);
}

/* ── タグ ── */
.dcard-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-top: 0.6rem;
}

.tag {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  color: var(--muted);
  padding: 0.15em 0.5em;
  border: 1px solid var(--border);
  border-radius: 100px;
}
</style>
