<template>
  <div
    class="article-card"
    :class="{ 'is-important': article.is_important }"
    :style="{ '--source-color': sourceColor }"
  >
    <div class="card-header">
      <span class="source-badge">{{ article.source.toUpperCase() }}</span>
      <div class="card-header-right">
        <span v-if="article.is_indexed" class="indexed-dot" title="RAGインデックス済">●</span>
        <button
          class="star-btn"
          :class="{ active: article.is_important }"
          :disabled="toggling"
          @click="onToggleImportant"
          :title="article.is_important ? '重要解除' : '重要マーク'"
        >{{ article.is_important ? '★' : '☆' }}</button>
      </div>
    </div>

    <a :href="article.url" target="_blank" rel="noopener" class="article-title">
      {{ article.title }}
    </a>

    <p v-if="article.summary" class="article-summary">{{ article.summary }}</p>

    <div class="card-footer">
      <div class="tags">
        <span v-for="tag in article.tags.slice(0, 3)" :key="tag" class="tag">#{{ tag }}</span>
      </div>
      <div class="card-meta">
        <span>{{ article.author ?? '—' }}</span>
        <span class="meta-sep">·</span>
        <span>{{ formatDate(article.published_at) }}</span>
        <template v-if="article.like_count > 0">
          <span class="meta-sep">·</span>
          <span>♥ {{ article.like_count }}</span>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Article } from '@/api/client'

const props = defineProps<{ article: Article }>()
const emit = defineEmits<{ (e: 'toggle-important', id: number): void }>()

const toggling = ref(false)

const sourceColor = computed(() => {
  const map: Record<string, string> = {
    qiita: 'var(--qiita)',
    zenn:  'var(--zenn)',
    note:  'var(--note)',
    arxiv: 'var(--arxiv)',
  }
  return map[props.article.source] ?? 'var(--muted)'
})

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' })
}

async function onToggleImportant() {
  toggling.value = true
  emit('toggle-important', props.article.id)
  toggling.value = false
}
</script>

<style scoped>
.article-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.1rem;
  position: relative;
  overflow: hidden;
  transition: border-color var(--t), transform var(--t), box-shadow var(--t);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.article-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--source-color, var(--border));
}

.article-card:hover {
  border-color: var(--border-2);
  transform: translateY(-2px);
  box-shadow: 0 10px 36px rgba(0, 0, 0, 0.45);
}

.article-card.is-important {
  border-color: rgba(255, 200, 87, 0.28);
  background: linear-gradient(140deg, var(--surface) 70%, rgba(255, 200, 87, 0.04) 100%);
}

/* ── Card header ── */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.7rem;
}

.card-header-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.source-badge {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  font-weight: 500;
  letter-spacing: 0.1em;
  padding: 0.18em 0.55em;
  border-radius: var(--radius-sm);
  color: var(--source-color, var(--muted));
  border: 1px solid var(--source-color, var(--border));
  background: transparent;
  opacity: 0.8;
}

.indexed-dot {
  font-size: 0.45rem;
  color: var(--accent);
  opacity: 0.6;
  line-height: 1;
}

.star-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--muted);
  font-size: 0.95rem;
  padding: 0.2rem 0.25rem;
  line-height: 1;
  transition: color var(--t), transform var(--t);
  border-radius: var(--radius-sm);
}

.star-btn:hover:not(:disabled) {
  color: var(--gold);
  transform: scale(1.25);
}

.star-btn.active {
  color: var(--gold);
  filter: drop-shadow(0 0 6px rgba(255, 200, 87, 0.5));
}

.star-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ── Title ── */
.article-title {
  font-family: var(--font-title);
  font-size: 0.95rem;
  font-style: italic;
  font-weight: 600;
  line-height: 1.5;
  color: var(--text);
  display: block;
  margin-bottom: 0.55rem;
  flex: 1;
  transition: color var(--t);
}

.article-title:hover {
  color: var(--accent);
}

/* ── Summary ── */
.article-summary {
  font-size: 0.78rem;
  line-height: 1.65;
  color: var(--muted);
  margin-bottom: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ── Footer ── */
.card-footer {
  margin-top: auto;
  padding-top: 0.65rem;
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.tag {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  color: var(--muted);
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 0.08em 0.5em;
  transition: color var(--t);
}

.tag:hover {
  color: var(--text);
}

.card-meta {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 0.3rem;
  white-space: nowrap;
}

.meta-sep {
  opacity: 0.4;
}
</style>
