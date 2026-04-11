<template>
  <v-card :elevation="article.is_important ? 3 : 1" :class="{ 'border-primary': article.is_important }">
    <v-card-item>
      <template #prepend>
        <v-chip
          :color="sourceColor"
          size="small"
          class="mr-2"
          label
        >
          {{ article.source.toUpperCase() }}
        </v-chip>
      </template>
      <template #append>
        <v-btn
          :icon="article.is_important ? 'mdi-star' : 'mdi-star-outline'"
          :color="article.is_important ? 'amber' : 'grey'"
          variant="text"
          size="small"
          :loading="toggling"
          @click="onToggleImportant"
        />
      </template>
    </v-card-item>

    <v-card-text class="pb-1">
      <a :href="article.url" target="_blank" rel="noopener" class="text-body-1 font-weight-medium text-primary">
        {{ article.title }}
      </a>
      <div v-if="article.summary" class="text-body-2 text-medium-emphasis mt-1 text-truncate-3">
        {{ article.summary }}
      </div>
    </v-card-text>

    <v-card-actions class="pt-0 flex-wrap">
      <v-chip
        v-for="tag in article.tags.slice(0, 3)"
        :key="tag"
        size="x-small"
        variant="tonal"
        class="mr-1 mb-1"
      >
        {{ tag }}
      </v-chip>
      <v-spacer />
      <span class="text-caption text-medium-emphasis">
        <v-icon size="x-small">mdi-account</v-icon>
        {{ article.author ?? '—' }}
        &nbsp;·&nbsp;
        {{ formatDate(article.published_at) }}
      </span>
      <v-chip v-if="article.like_count > 0" size="x-small" variant="text" class="ml-1">
        <v-icon start size="x-small">mdi-thumb-up-outline</v-icon>
        {{ article.like_count }}
      </v-chip>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Article } from '@/api/client'

const props = defineProps<{ article: Article }>()
const emit = defineEmits<{ (e: 'toggle-important', id: number): void }>()

const toggling = ref(false)

const sourceColor = computed(() => {
  const map: Record<string, string> = {
    qiita: 'green',
    zenn: 'blue',
    note: 'orange',
    arxiv: 'purple',
  }
  return map[props.article.source] ?? 'grey'
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
.text-truncate-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.border-primary {
  border-left: 3px solid rgb(var(--v-theme-primary));
}
</style>
