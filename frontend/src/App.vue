<template>
  <v-app>
    <v-app-bar color="primary" elevation="2">
      <v-app-bar-title>
        <router-link to="/" class="text-white text-decoration-none font-weight-bold">
          Tech News Search
        </router-link>
      </v-app-bar-title>
      <template #append>
        <v-btn icon to="/" title="トレンド">
          <v-icon>mdi-newspaper-variant-outline</v-icon>
        </v-btn>
        <v-btn icon to="/important" title="重要記事">
          <v-icon>mdi-star-outline</v-icon>
        </v-btn>
        <v-btn icon to="/search" title="RAG検索">
          <v-icon>mdi-magnify</v-icon>
        </v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container fluid class="pa-4">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
</script>

<style>
a {
  color: inherit;
}
</style>
