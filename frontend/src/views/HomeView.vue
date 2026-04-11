<template>
  <div>
    <!-- 統計バー -->
    <v-row class="mb-4" dense>
      <v-col v-for="stat in statCards" :key="stat.label" cols="6" sm="3">
        <v-card variant="tonal" :color="stat.color" rounded="lg">
          <v-card-text class="pa-3 text-center">
            <div class="text-h5 font-weight-bold">{{ stat.value }}</div>
            <div class="text-caption">{{ stat.label }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <div class="d-flex align-center mb-3">
      <h1 class="text-h5 font-weight-bold">トレンド</h1>
      <v-chip class="ml-3" size="small" color="primary" variant="tonal">
        {{ store.total }} 件
      </v-chip>
    </div>

    <SourceFilter
      v-model:sources="store.selectedSources"
      v-model:language="store.selectedLanguage"
      @update:sources="onFilterChange"
      @update:language="onFilterChange"
    />

    <v-alert v-if="store.error" type="error" class="mb-4" closable>
      {{ store.error }}
    </v-alert>

    <div v-if="store.loading" class="d-flex justify-center py-8">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <template v-else>
      <v-row>
        <v-col
          v-for="article in store.items"
          :key="article.id"
          cols="12"
          sm="6"
          lg="4"
        >
          <ArticleCard :article="article" @toggle-important="onToggleImportant" />
        </v-col>
      </v-row>

      <div v-if="store.items.length === 0" class="text-center py-12 text-medium-emphasis">
        <v-icon size="64" class="mb-4">mdi-newspaper-variant-outline</v-icon>
        <div>記事がありません。「今すぐ収集」を押して収集を開始してください。</div>
      </div>

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
import { computed, onMounted, ref, watch } from 'vue'
import ArticleCard from '@/components/ArticleCard.vue'
import SourceFilter from '@/components/SourceFilter.vue'
import { useArticlesStore } from '@/stores/articles'
import { statsApi, type StatsOverview } from '@/api/client'

const store = useArticlesStore()
const stats = ref<StatsOverview | null>(null)

const statCards = computed(() => {
  if (!stats.value) return []
  const sourceMap = Object.fromEntries(stats.value.by_source.map((s) => [s.source, s.count]))
  return [
    { label: '総記事数', value: stats.value.total_articles, color: 'primary' },
    { label: '重要マーク', value: stats.value.important_articles, color: 'amber' },
    { label: 'RAG登録済', value: stats.value.indexed_articles, color: 'green' },
    {
      label: 'arXiv論文',
      value: sourceMap['arxiv'] ?? 0,
      color: 'purple',
    },
  ]
})

async function loadStats() {
  try {
    const resp = await statsApi.overview()
    stats.value = resp.data
  } catch {
    // 無視
  }
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
