<template>
  <v-row align="center" class="mb-2">
    <v-col cols="12" sm="auto">
      <v-btn-toggle v-model="selectedSources" multiple color="primary" density="compact" variant="outlined">
        <v-btn value="qiita" size="small">Qiita</v-btn>
        <v-btn value="zenn" size="small">Zenn</v-btn>
        <v-btn value="note" size="small">Note</v-btn>
        <v-btn value="arxiv" size="small">arXiv</v-btn>
      </v-btn-toggle>
    </v-col>
    <v-col cols="12" sm="auto">
      <v-btn-toggle v-model="selectedLanguage" color="primary" density="compact" variant="outlined">
        <v-btn value="" size="small">すべて</v-btn>
        <v-btn value="ja" size="small">日本語</v-btn>
        <v-btn value="en" size="small">English</v-btn>
      </v-btn-toggle>
    </v-col>
    <v-col cols="12" sm="auto" class="ml-auto">
      <v-btn
        prepend-icon="mdi-refresh"
        size="small"
        variant="tonal"
        :loading="collecting"
        @click="collectNow"
      >
        今すぐ収集
      </v-btn>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { collectorApi } from '@/api/client'

const selectedSources = defineModel<string[]>('sources', { default: () => [] })
const selectedLanguage = defineModel<string>('language', { default: '' })

const collecting = ref(false)

async function collectNow() {
  collecting.value = true
  try {
    await collectorApi.runAll()
  } finally {
    collecting.value = false
  }
}
</script>
