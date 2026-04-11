<template>
  <div>
    <div class="d-flex align-center mb-4">
      <h1 class="text-h5 font-weight-bold">
        <v-icon class="mr-2">mdi-magnify</v-icon>RAG検索
      </h1>
      <v-chip v-if="indexedCount > 0" class="ml-3" size="small" color="primary" variant="tonal">
        {{ indexedCount }} 件インデックス済み
      </v-chip>
    </div>

    <!-- 検索ボックス -->
    <v-card class="mb-6" elevation="1">
      <v-card-text>
        <v-textarea
          v-model="query"
          label="質問を入力してください"
          placeholder="例: RAGのチャンキング戦略について教えて"
          rows="2"
          auto-grow
          variant="outlined"
          hide-details
          :loading="loading"
          @keydown.ctrl.enter="search"
          @keydown.meta.enter="search"
        />
        <div class="d-flex align-center mt-3 gap-3 flex-wrap">
          <!-- ソースフィルタ -->
          <v-btn-toggle v-model="filterSources" multiple density="compact" variant="outlined" color="primary">
            <v-btn value="qiita" size="small">Qiita</v-btn>
            <v-btn value="zenn" size="small">Zenn</v-btn>
            <v-btn value="note" size="small">Note</v-btn>
            <v-btn value="arxiv" size="small">arXiv</v-btn>
          </v-btn-toggle>
          <!-- 言語フィルタ -->
          <v-btn-toggle v-model="filterLanguage" density="compact" variant="outlined" color="primary">
            <v-btn value="" size="small">すべて</v-btn>
            <v-btn value="ja" size="small">日本語</v-btn>
            <v-btn value="en" size="small">English</v-btn>
          </v-btn-toggle>
          <v-spacer />
          <v-btn
            color="primary"
            prepend-icon="mdi-send"
            :loading="loading"
            :disabled="!query.trim()"
            @click="search"
          >
            検索 <span class="text-caption ml-1 opacity-70">(Ctrl+Enter)</span>
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <!-- インデックス未登録の警告 -->
    <v-alert v-if="indexedCount === 0" type="info" variant="tonal" class="mb-4">
      重要マーク（☆）をつけた記事が自動的にインデックスに登録されます。まずはトレンド画面で記事を確認してください。
    </v-alert>

    <!-- エラー -->
    <v-alert v-if="error" type="error" variant="tonal" class="mb-4" closable @click:close="error = null">
      {{ error }}
    </v-alert>

    <!-- 検索結果 -->
    <template v-if="result">
      <v-card class="mb-4" color="primary" variant="tonal">
        <v-card-title class="text-body-1 font-weight-bold pb-0">
          <v-icon size="small" class="mr-1">mdi-robot-outline</v-icon>回答
        </v-card-title>
        <v-card-text class="text-body-1" style="white-space: pre-wrap;">{{ result.answer }}</v-card-text>
      </v-card>

      <div v-if="result.sources.length > 0" class="mb-6">
        <div class="text-subtitle-2 font-weight-bold mb-2 text-medium-emphasis">
          <v-icon size="small">mdi-book-open-outline</v-icon> 参照元 ({{ result.sources.length }} 件)
        </div>
        <v-list lines="two" density="compact" rounded="lg" border>
          <v-list-item
            v-for="src in result.sources"
            :key="src.article_id"
            :href="src.url"
            target="_blank"
            rel="noopener"
            :title="src.title"
            prepend-icon="mdi-file-document-outline"
          >
            <template #append>
              <v-chip size="x-small" :color="scoreColor(src.relevance_score)" variant="tonal">
                {{ (src.relevance_score * 100).toFixed(0) }}%
              </v-chip>
            </template>
          </v-list-item>
        </v-list>
      </div>
    </template>

    <!-- 検索履歴 -->
    <div v-if="history.length > 0">
      <div class="text-subtitle-2 font-weight-bold mb-2 text-medium-emphasis">
        <v-icon size="small">mdi-history</v-icon> 検索履歴
      </div>
      <v-list density="compact" rounded="lg" border>
        <v-list-item
          v-for="h in history"
          :key="h.id"
          :subtitle="formatDate(h.searched_at)"
          @click="loadHistory(h)"
          style="cursor: pointer"
        >
          <template #title>
            <span class="text-body-2">{{ h.query }}</span>
          </template>
          <template #prepend>
            <v-icon size="small" color="grey">mdi-magnify</v-icon>
          </template>
        </v-list-item>
      </v-list>
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
  } catch {
    // 履歴取得失敗は無視
  }
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
  if (score >= 0.8) return 'success'
  if (score >= 0.6) return 'warning'
  return 'grey'
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('ja-JP', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  await fetchHistory()
  // インデックス済み件数を取得
  try {
    const resp = await statsApi.overview()
    indexedCount.value = resp.data.indexed_articles
  } catch {
    // 無視
  }
})
</script>
