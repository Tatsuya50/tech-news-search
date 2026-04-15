import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  paramsSerializer: (params) => {
    const parts: string[] = []
    for (const [key, value] of Object.entries(params)) {
      if (value === undefined || value === null) continue
      if (Array.isArray(value)) {
        // FastAPI が期待する繰り返し形式: source=qiita&source=zenn
        for (const v of value) parts.push(`${key}=${encodeURIComponent(v)}`)
      } else {
        parts.push(`${key}=${encodeURIComponent(String(value))}`)
      }
    }
    return parts.join('&')
  },
})

export interface Article {
  id: number
  source: string
  title: string
  url: string
  summary: string | null
  author: string | null
  published_at: string
  collected_at: string
  tags: string[]
  like_count: number
  is_important: boolean
  is_indexed: boolean
  language: string
}

export interface ArticleListResponse {
  items: Article[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface StatsOverview {
  total_articles: number
  important_articles: number
  indexed_articles: number
  by_source: { source: string; count: number }[]
}

export interface RagSearchResponse {
  answer: string
  sources: { article_id: number; title: string; url: string; relevance_score: number }[]
  searched_at: string
}

export const articlesApi = {
  list(params: {
    source?: string[]
    language?: string
    tags?: string[]
    is_important?: boolean
    keyword?: string
    page?: number
    per_page?: number
  }) {
    return apiClient.get<ArticleListResponse>('/articles', { params })
  },

  toggleImportant(id: number) {
    return apiClient.patch<Article>(`/articles/${id}/important`)
  },
}

export const collectorApi = {
  runAll() {
    return apiClient.post('/collector/run')
  },
  runSource(source: string) {
    return apiClient.post(`/collector/run/${source}`)
  },
}

export const statsApi = {
  overview() {
    return apiClient.get<StatsOverview>('/stats/overview')
  },
}

export interface ArxivArticleDigest {
  id: number
  title: string
  url: string
  author: string | null
  published_at: string
  summary: string | null
  summary_ja: string | null
  tags: string[]
}

export interface ArxivDailyDigestResponse {
  date: string
  articles: ArxivArticleDigest[]
  total_count: number
  overall_digest: string | null
}

export const digestApi = {
  getArxivToday() {
    return apiClient.get<ArxivDailyDigestResponse>('/digest/arxiv/today', { timeout: 120000 })
  },
}

export interface SearchHistoryItem {
  id: number
  query: string
  answer: string
  searched_at: string
}

export const ragApi = {
  search(query: string, topK = 5, filterSource?: string[], filterLanguage?: string) {
    return apiClient.post<RagSearchResponse>('/rag/search', {
      query,
      top_k: topK,
      filter_source: filterSource?.length ? filterSource : undefined,
      filter_language: filterLanguage || undefined,
    })
  },
  getHistory() {
    return apiClient.get<SearchHistoryItem[]>('/rag/history')
  },
  getDocuments() {
    return apiClient.get<{ id: number; article_id: number; chunk_index: number; indexed_at: string }[]>('/rag/documents')
  },
}
