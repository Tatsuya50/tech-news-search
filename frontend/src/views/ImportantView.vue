<template>
  <div>
    <div class="d-flex align-center mb-4">
      <h1 class="text-h5 font-weight-bold">
        <v-icon color="amber" class="mr-2">mdi-star</v-icon>重要記事
      </h1>
      <v-chip class="ml-3" size="small" color="amber" variant="tonal">
        {{ store.total }} 件
      </v-chip>
    </div>

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
          <ArticleCard :article="article" @toggle-important="store.toggleImportant" />
        </v-col>
      </v-row>

      <div v-if="store.items.length === 0" class="text-center py-12 text-medium-emphasis">
        <v-icon size="64" class="mb-4">mdi-star-outline</v-icon>
        <div>重要マークをつけた記事がここに表示されます。</div>
      </div>

      <v-pagination
        v-if="store.totalPages > 1"
        v-model="store.page"
        :length="store.totalPages"
        class="mt-6"
        @update:model-value="store.fetchArticles(true)"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import ArticleCard from '@/components/ArticleCard.vue'
import { useArticlesStore } from '@/stores/articles'

const store = useArticlesStore()

onMounted(() => {
  store.fetchArticles(true)
})
</script>
