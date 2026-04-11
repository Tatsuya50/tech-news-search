<template>
  <div class="search-wrap">
    <!-- Header -->
    <div class="search-heading">
      <span class="search-heading-label">RAG SEARCH</span>
      <span v-if="indexedCount > 0" class="indexed-badge">{{ indexedCount }} indexed</span>
    </div>

    <!-- Input box -->
    <div class="search-box" :class="{ focused: isFocused }">
      <textarea
        ref="inputEl"
        v-model="query"
        class="search-input"
        placeholder="質問を入力してください — 例: RAGのチャンキング戦略について"
        rows="2"
        @focus="isFocused = true"
        @blur="isFocused = false"
        @keydown.ctrl.enter="search"
        @keydown.meta.enter="search"
      />
      <div class="search-controls">
        <!-- Source filters -->
        <div class="filter-group">
          <button
            v-for="src in sourceOptions"
            :key="src.value"
            class="mini-pill"
            :class="{ active: filterSources.includes(src.value) }"
            :style="filterSources.includes(src.value) ? { '--pill-color': src.color } : {}"
            @click="toggleSource(src.value)"
          >{{ src.label }}</button>
        </div>
        <!-- Language -->
        <div class="filter-group">
          <button
            v-for="lang in langOptions"
            :key="lang.value"
            class="mini-pill"
            :class="{ active: filterLanguage === lang.value }"
            @click="filterLanguage = lang.value"
          >{{ lang.label }}</button>
        </div>
        <div style="margin-left: auto; display: flex; align-items: center; gap: 0.5rem;">
          <span class="hint-text">Ctrl+↵</span>
          <button
            class="search-btn"
            :disabled="!query.trim() || loading"
            @click="search"
          >
            <span v-if="!loading">SEARCH →</span>
            <span v-else class="searching-text">···</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Alert: no index -->
    <div v-if="indexedCount === 0" class="info-bar">
      ◎ 重要マーク（★）をつけた記事がRAGに自動登録されます。まずFEEDで記事を保存してください。
    </div>

    <!-- Error -->
    <div v-if="error" class="error-bar">
      <span>{{ error }}</span>
      <button class="error-close" @click="error = null">✕</button>
    </div>

    <!-- Answer -->
    <div v-if="result" class="answer-block">
      <div class="answer-header">
        <span class="answer-label">◈ AI SIGNAL</span>
        <span class="answer-time">{{ formatTime(result.searched_at) }}</span>
      </div>
      <div class="answer-body">{{ result.answer }}</div>
    </div>

    <!-- Sources -->
    <template v-if="result && result.sources.length > 0">
      <div class="sources-heading">SOURCES ({{ result.sources.length }})</div>
      <a
        v-for="(src, i) in result.sources"
        :key="src.article_id"
        :href="src.url"
        target="_blank"
        rel="noopener"
        class="source-row"
      >
        <span class="source-num">{{ String(i + 1).padStart(2, '0') }}</span>
        <span class="source-title">{{ src.title }}</span>
        <span class="source-score" :style="{ color: scoreColor(src.relevance_score) }">
          {{ (src.relevance_score * 100).toFixed(0) }}%
        </span>
      </a>
    </template>

    <!-- History -->
    <div v-if="history.length > 0" class="history-section">
      <div class="history-heading">HISTORY</div>
      <div
        v-for="h in history"
        :key="h.id"
        class="history-row"
        @click="loadHistory(h)"
      >
        <span class="history-icon">◎</span>
        <span class="history-query">{{ h.query }}</span>
        <span class="history-date">{{ formatDate(h.searched_at) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ragApi, statsApi, type RagSearchResponse, type SearchHistoryItem } from '@/api/client'

const query = ref('')
const filterSources = ref<string[]>([])
const filterLanguage = ref('')
const loading = ref(false)
const error = ref<string | null>(null)
const result = ref<RagSearchResponse | null>(null)
const history = ref<SearchHistoryItem[]>([])
const indexedCount = ref(0)
const isFocused = ref(false)
const inputEl = ref<HTMLTextAreaElement | null>(null)

const sourceOptions = [
  { value: 'qiita', label: 'Qiita', color: 'var(--qiita)' },
  { value: 'zenn',  label: 'Zenn',  color: 'var(--zenn)'  },
  { value: 'note',  label: 'Note',  color: 'var(--note)'  },
  { value: 'arxiv', label: 'arXiv', color: 'var(--arxiv)' },
]

const langOptions = [
  { value: '',   label: 'ALL' },
  { value: 'ja', label: 'JA'  },
  { value: 'en', label: 'EN'  },
]

function toggleSource(val: string) {
  const idx = filterSources.value.indexOf(val)
  if (idx === -1) filterSources.value = [...filterSources.value, val]
  else filterSources.value = filterSources.value.filter((s) => s !== val)
}

async function search() {
  if (!query.value.trim()) return
  loading.value = true
  error.value = null
  result.value = null
  try {
    const resp = await ragApi.search(
      query.value.trim(),
      5,
      filterSources.value,
      filterLanguage.value,
    )
    result.value = resp.data
    await fetchHistory()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '検索に失敗しました'
  } finally {
    loading.value = false
  }
}

async function fetchHistory() {
  try {
    const resp = await ragApi.getHistory()
    history.value = resp.data
  } catch { /* ignore */ }
}

function loadHistory(h: SearchHistoryItem) {
  query.value = h.query
  result.value = {
    answer: h.answer,
    sources: [],
    searched_at: h.searched_at,
  }
}

function scoreColor(score: number) {
  if (score >= 0.8) return 'var(--accent)'
  if (score >= 0.6) return 'var(--gold)'
  return 'var(--muted)'
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('ja-JP', {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

onMounted(async () => {
  await fetchHistory()
  try {
    const resp = await statsApi.overview()
    indexedCount.value = resp.data.indexed_articles
  } catch { /* ignore */ }
})
</script>

<style scoped>
.search-wrap {
  max-width: 820px;
  margin: 0 auto;
}

/* ── Heading ── */
.search-heading {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.search-heading-label {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted);
  position: relative;
}

.search-heading-label::after {
  content: '';
  position: absolute;
  left: calc(100% + 0.75rem);
  top: 50%;
  width: 60vw;
  height: 1px;
  background: var(--border);
}

.indexed-badge {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--accent);
  border: 1px solid var(--accent);
  border-radius: 100px;
  padding: 0.15em 0.65em;
  background: var(--accent-dim);
  position: relative;
  z-index: 1;
}

/* ── Search box ── */
.search-box {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  margin-bottom: 1rem;
  transition: border-color var(--t), box-shadow var(--t);
  overflow: hidden;
}

.search-box.focused {
  border-color: var(--accent);
  box-shadow: 0 0 0 1px var(--accent), 0 0 24px var(--accent-glow);
}

.search-input {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text);
  font-family: var(--font-ui);
  font-size: 0.95rem;
  padding: 1rem 1.2rem 0.75rem;
  resize: none;
  line-height: 1.6;
  display: block;
}

.search-input::placeholder {
  color: var(--muted);
  font-style: italic;
}

.search-controls {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1rem;
  border-top: 1px solid var(--border);
  flex-wrap: wrap;
  background: var(--surface-2);
}

.filter-group {
  display: flex;
  gap: 0.2rem;
}

.mini-pill {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  letter-spacing: 0.05em;
  padding: 0.25em 0.6em;
  border-radius: 100px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  transition: all var(--t);
  line-height: 1.4;
}

.mini-pill:hover {
  color: var(--text);
  border-color: var(--border-2);
}

.mini-pill.active {
  border-color: var(--pill-color, var(--accent));
  color: var(--pill-color, var(--accent));
  background: rgba(200, 255, 94, 0.06);
}

.hint-text {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  color: var(--muted);
  opacity: 0.6;
}

.search-btn {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  letter-spacing: 0.1em;
  font-weight: 500;
  padding: 0.45em 1.2em;
  border-radius: var(--radius-sm);
  border: 1px solid var(--accent);
  background: var(--accent);
  color: var(--bg);
  cursor: pointer;
  transition: all var(--t);
  min-width: 5.5rem;
  text-align: center;
}

.search-btn:hover:not(:disabled) {
  box-shadow: 0 0 20px var(--accent-glow);
}

.search-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.searching-text {
  animation: pulse 0.8s ease infinite;
  display: inline-block;
  letter-spacing: 0.2em;
}

/* ── Info bar ── */
.info-bar {
  background: rgba(200, 255, 94, 0.05);
  border: 1px solid rgba(200, 255, 94, 0.15);
  border-radius: var(--radius);
  color: var(--muted);
  font-family: var(--font-mono);
  font-size: 0.72rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  line-height: 1.5;
}

/* ── Answer block ── */
.answer-block {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 1.5rem;
  animation: fadeUp 0.3s ease;
}

.answer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 1rem;
  border-bottom: 1px solid var(--border);
  background: var(--accent-dim);
}

.answer-label {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
}

.answer-time {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--muted);
}

.answer-body {
  padding: 1.1rem 1.25rem;
  font-size: 0.88rem;
  line-height: 1.75;
  color: var(--text);
  white-space: pre-wrap;
}

/* ── Sources ── */
.sources-heading {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  letter-spacing: 0.12em;
  color: var(--muted);
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.source-row {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 0.65rem 0.9rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  margin-bottom: 0.35rem;
  color: var(--text);
  text-decoration: none;
  transition: all var(--t);
}

.source-row:hover {
  border-color: var(--border-2);
  background: var(--surface-2);
}

.source-num {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--muted);
  min-width: 1.4rem;
  flex-shrink: 0;
}

.source-title {
  flex: 1;
  font-family: var(--font-title);
  font-style: italic;
  font-size: 0.88rem;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.source-score {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  font-weight: 500;
  flex-shrink: 0;
}

/* ── History ── */
.history-section {
  margin-top: 2rem;
}

.history-heading {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  letter-spacing: 0.12em;
  color: var(--muted);
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.history-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.55rem 0.75rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  border: 1px solid transparent;
  transition: all var(--t);
}

.history-row:hover {
  background: var(--surface);
  border-color: var(--border);
}

.history-icon {
  font-size: 0.55rem;
  color: var(--muted);
  flex-shrink: 0;
}

.history-query {
  flex: 1;
  font-size: 0.85rem;
  color: var(--text);
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.history-date {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--muted);
  flex-shrink: 0;
}
</style>
