<template>
  <div class="filter-bar">
    <div class="filter-group">
      <button
        v-for="src in sources"
        :key="src.value"
        class="filter-pill"
        :class="{ active: selectedSources.includes(src.value) }"
        :style="selectedSources.includes(src.value) ? { '--pill-color': src.color } : {}"
        @click="toggleSource(src.value)"
      >
        {{ src.label }}
      </button>
    </div>

    <div class="filter-divider" />

    <div class="filter-group">
      <button
        v-for="lang in langs"
        :key="lang.value"
        class="filter-pill"
        :class="{ active: selectedLanguage === lang.value }"
        @click="selectedLanguage = lang.value"
      >
        {{ lang.label }}
      </button>
    </div>

    <button class="collect-btn" :disabled="collecting" @click="collectNow">
      <span v-if="!collecting">↺ 収集</span>
      <span v-else class="collecting-text">...</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { collectorApi } from '@/api/client'

const selectedSources = defineModel<string[]>('sources', { default: () => [] })
const selectedLanguage = defineModel<string>('language', { default: '' })

const collecting = ref(false)

const sources = [
  { value: 'qiita', label: 'Qiita',  color: 'var(--qiita)' },
  { value: 'zenn',  label: 'Zenn',   color: 'var(--zenn)'  },
  { value: 'note',  label: 'Note',   color: 'var(--note)'  },
  { value: 'arxiv', label: 'arXiv',  color: 'var(--arxiv)' },
]

const langs = [
  { value: '',   label: 'ALL' },
  { value: 'ja', label: 'JA'  },
  { value: 'en', label: 'EN'  },
]

function toggleSource(val: string) {
  const idx = selectedSources.value.indexOf(val)
  if (idx === -1) selectedSources.value = [...selectedSources.value, val]
  else selectedSources.value = selectedSources.value.filter((s) => s !== val)
}

async function collectNow() {
  collecting.value = true
  try {
    await collectorApi.runAll()
  } finally {
    collecting.value = false
  }
}
</script>

<style scoped>
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 1.25rem;
  padding: 0.65rem 0.9rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.filter-group {
  display: flex;
  gap: 0.2rem;
}

.filter-pill {
  font-family: var(--font-mono);
  font-size: 0.67rem;
  letter-spacing: 0.06em;
  padding: 0.3em 0.75em;
  border-radius: 100px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  transition: all var(--t);
  line-height: 1.4;
}

.filter-pill:hover {
  color: var(--text);
  border-color: var(--border-2);
}

.filter-pill.active {
  background: var(--accent-dim);
  border-color: var(--pill-color, var(--accent));
  color: var(--pill-color, var(--accent));
}

.filter-divider {
  width: 1px;
  height: 18px;
  background: var(--border);
  align-self: center;
  flex-shrink: 0;
}

.collect-btn {
  margin-left: auto;
  font-family: var(--font-mono);
  font-size: 0.67rem;
  letter-spacing: 0.07em;
  padding: 0.32em 1em;
  border-radius: 100px;
  border: 1px solid var(--accent);
  background: var(--accent-dim);
  color: var(--accent);
  cursor: pointer;
  transition: all var(--t);
  min-width: 4rem;
  text-align: center;
}

.collect-btn:hover:not(:disabled) {
  background: var(--accent);
  color: var(--bg);
}

.collect-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.collecting-text {
  animation: pulse 1s ease infinite;
  display: inline-block;
}

@media (max-width: 600px) {
  .filter-bar {
    flex-direction: column;
    align-items: flex-start;
  }
  .collect-btn {
    margin-left: 0;
  }
}
</style>
