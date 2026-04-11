<template>
  <div>
    <div class="page-heading">
      <span class="page-title">★ Saved Articles</span>
      <span class="page-count">{{ store.total }} 件</span>
    </div>

    <div v-if="store.loading" class="loading-state">
      <div class="spinner" />
    </div>

    <template v-else>
      <div v-if="store.items.length > 0" class="article-grid">
        <ArticleCard
          v-for="article in store.items"
          :key="article.id"
          :article="article"
          @toggle-important="store.toggleImportant"
        />
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">☆</div>
        <div class="empty-text">MARK ARTICLES WITH ★ TO SAVE THEM HERE</div>
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
