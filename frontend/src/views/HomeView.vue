<template>
  <div>
    <!-- Stats strip -->
    <div v-if="stats" class="stat-strip">
      <div class="stat-card">
        <div class="stat-number">{{ stats.total_articles.toLocaleString() }}</div>
        <div class="stat-label">TOTAL</div>
      </div>
      <div class="stat-card">
        <div class="stat-number gold">{{ stats.important_articles }}</div>
        <div class="stat-label">SAVED</div>
      </div>
      <div class="stat-card">
        <div class="stat-number accent">{{ stats.indexed_articles }}</div>
        <div class="stat-label">INDEXED</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ arxivCount }}</div>
        <div class="stat-label">ARXIV</div>
      </div>
    </div>

    <!-- Page heading -->
    <div class="page-heading">
      <span class="page-title">Intelligence Feed</span>
      <span class="page-count">{{ store.total }} 件</span>
    </div>

    <!-- Keyword search -->
    <div class="keyword-search">
      <input
        v-model="store.searchKeyword"
        class="keyword-input"
        type="search"
        placeholder="キーワードで検索（タイトル・本文）"
        @keydown.enter="onFilterChange"
        @input="onKeywordInput"
      />
      <button
        v-if="store.searchKeyword"
        class="keyword-clear"
        @click="clearKeyword"
      >✕</button>
      <button class="keyword-btn" @click="onFilterChange">検索</button>
    </div>

    <!-- Filters -->
    <SourceFilter
      v-model:sources="store.selectedSources"
      v-model:language="store.selectedLanguage"
      @update:sources="onFilterChange"
      @update:language="onFilterChange"
    />

    <!-- Error -->
    <div v-if="store.error" class="error-bar">
      <span>{{ store.error }}</span>
      <button class="error-close" @click="store.error = null">✕</button>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="loading-state">
      <div class="spinner" />
    </div>

    <template v-else>
      <!-- Articles -->
      <div v-if="store.items.length > 0" class="article-grid">
        <ArticleCard
          v-for="article in store.items"
          :key="article.id"
          :article="article"
          @toggle-important="onToggleImportant"
        />
      </div>

      <!-- Empty -->
      <div v-else class="empty-state">
        <div class="empty-icon">◈</div>
        <div class="empty-text">NO ARTICLES YET — CLICK ↺ 収集 TO FETCH</div>
      </div>

      <!-- Pagination -->
      <v-pagination
        v-if="store.totalPages > 1"
        v-model="store.page"
        :length="store.totalPages"
        class="mt-6"
        @update:model-value="store.fetchArticles()"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { ref } from 'vue'
import ArticleCard from '@/components/ArticleCard.vue'
import SourceFilter from '@/components/SourceFilter.vue'
import { useArticlesStore } from '@/stores/articles'
import { statsApi, type StatsOverview } from '@/api/client'

const store = useArticlesStore()
const stats = ref<StatsOverview | null>(null)

const arxivCount = computed(() => {
  if (!stats.value) return 0
  return stats.value.by_source.find((s) => s.source === 'arxiv')?.count ?? 0
})

async function loadStats() {
  try {
    const resp = await statsApi.overview()
    stats.value = resp.data
  } catch { /* ignore */ }
}

async function onToggleImportant(id: number) {
  await store.toggleImportant(id)
  await loadStats()
}

function onFilterChange() {
  store.page = 1
  store.fetchArticles()
}

let keywordTimer: ReturnType<typeof setTimeout> | null = null
function onKeywordInput() {
  if (keywordTimer) clearTimeout(keywordTimer)
  keywordTimer = setTimeout(() => onFilterChange(), 400)
}

function clearKeyword() {
  store.searchKeyword = ''
  onFilterChange()
}

onMounted(async () => {
  await Promise.all([store.fetchArticles(), loadStats()])
})

watch(() => store.selectedLanguage, onFilterChange)
</script>

<style scoped>
/* ── Stats strip ── */
.stat-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem 0.75rem;
  text-align: center;
  transition: border-color var(--t);
}

.stat-card:hover {
  border-color: var(--border-2);
}

.stat-number {
  font-family: var(--font-ui);
  font-size: 1.75rem;
  font-weight: 800;
  line-height: 1;
  color: var(--text);
  margin-bottom: 0.3rem;
  letter-spacing: -0.02em;
}

.stat-number.accent { color: var(--accent); }
.stat-number.gold   { color: var(--gold); }

.stat-label {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  letter-spacing: 0.12em;
  color: var(--muted);
  text-transform: uppercase;
}

@media (max-width: 600px) {
  .stat-strip { grid-template-columns: repeat(2, 1fr); }
}

/* ── Keyword search ── */
.keyword-search {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.keyword-input {
  flex: 1;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-family: var(--font-ui);
  font-size: 0.88rem;
  padding: 0.5rem 0.85rem;
  outline: none;
  transition: border-color var(--t), box-shadow var(--t);
}

.keyword-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 1px var(--accent);
}

.keyword-input::placeholder {
  color: var(--muted);
}

.keyword-clear {
  background: transparent;
  border: none;
  color: var(--muted);
  font-size: 0.75rem;
  cursor: pointer;
  padding: 0.4rem 0.3rem;
  line-height: 1;
  transition: color var(--t);
}

.keyword-clear:hover {
  color: var(--text);
}

.keyword-btn {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  padding: 0.48em 1.1em;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-2);
  background: var(--surface-2);
  color: var(--text);
  cursor: pointer;
  transition: all var(--t);
  white-space: nowrap;
}

.keyword-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}
</style>
