import { defineStore } from 'pinia'
import { ref } from 'vue'
import { articlesApi, type Article, type ArticleListResponse } from '@/api/client'

export const useArticlesStore = defineStore('articles', () => {
  const items = ref<Article[]>([])
  const total = ref(0)
  const page = ref(1)
  const perPage = ref(20)
  const totalPages = ref(1)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const selectedSources = ref<string[]>([])
  const selectedLanguage = ref<string>('')
  const searchKeyword = ref<string>('')

  async function fetchArticles(isImportant?: boolean) {
    loading.value = true
    error.value = null
    try {
      const params: Record<string, unknown> = {
        page: page.value,
        per_page: perPage.value,
      }
      if (selectedSources.value.length > 0) params.source = selectedSources.value
      if (selectedLanguage.value) params.language = selectedLanguage.value
      if (isImportant !== undefined) params.is_important = isImportant
      if (searchKeyword.value.trim()) params.keyword = searchKeyword.value.trim()

      const resp = await articlesApi.list(params)
      const data: ArticleListResponse = resp.data
      items.value = data.items
      total.value = data.total
      totalPages.value = data.total_pages
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch articles'
    } finally {
      loading.value = false
    }
  }

  async function toggleImportant(id: number) {
    try {
      const resp = await articlesApi.toggleImportant(id)
      const updated = resp.data
      const idx = items.value.findIndex((a) => a.id === id)
      if (idx !== -1) items.value[idx] = updated
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to update'
    }
  }

  return {
    items,
    total,
    page,
    perPage,
    totalPages,
    loading,
    error,
    selectedSources,
    selectedLanguage,
    searchKeyword,
    fetchArticles,
    toggleImportant,
  }
})
