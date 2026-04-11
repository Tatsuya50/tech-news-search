<template>
  <v-app>
    <v-app-bar flat :elevation="0" height="54" color="#080810" class="app-bar">
      <div class="header-inner">
        <router-link to="/" class="brand">
          <span class="brand-mark">◈</span>
          <span class="brand-name">TNS</span>
          <span class="brand-sub">TECH·NEWS·SIGNAL</span>
        </router-link>
        <nav class="app-nav">
          <router-link to="/" class="nav-link" exact-active-class="nav-active">FEED</router-link>
          <router-link to="/important" class="nav-link" active-class="nav-active">SAVED</router-link>
          <router-link to="/search" class="nav-link" active-class="nav-active">SEARCH</router-link>
        </nav>
      </div>
    </v-app-bar>

    <v-main>
      <div class="main-content">
        <router-view />
      </div>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
</script>

<style scoped>
.app-bar {
  backdrop-filter: blur(12px);
  background: rgba(8, 8, 16, 0.92) !important;
}

.header-inner {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 54px;
}

.brand {
  display: flex;
  align-items: baseline;
  gap: 0.45rem;
  text-decoration: none;
}

.brand-mark {
  font-size: 1.2rem;
  color: var(--accent);
  line-height: 1;
  transform: translateY(1px);
  display: inline-block;
}

.brand-name {
  font-family: var(--font-ui);
  font-weight: 800;
  font-size: 1.05rem;
  color: var(--text);
  letter-spacing: 0.06em;
}

.brand-sub {
  font-family: var(--font-mono);
  font-size: 0.52rem;
  color: var(--muted);
  letter-spacing: 0.14em;
  padding-bottom: 1px;
}

.app-nav {
  display: flex;
  gap: 0.15rem;
}

.nav-link {
  font-family: var(--font-mono);
  font-size: 0.67rem;
  letter-spacing: 0.1em;
  padding: 0.4em 0.85em;
  border-radius: var(--radius-sm);
  color: var(--muted);
  transition: color var(--t), background var(--t);
}

.nav-link:hover {
  color: var(--text);
  background: var(--surface);
}

.nav-active {
  color: var(--accent) !important;
  background: var(--accent-dim) !important;
}
</style>
