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
</style>
