import '@mdi/font/css/materialdesignicons.css'
// @ts-expect-error vuetify styles side-effect import
import 'vuetify/styles'
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import App from './App.vue'
import router from './router'

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'dark',
    themes: {
      dark: {
        dark: true,
        colors: {
          background: '#080810',
          surface: '#0e0e1c',
          primary: '#c8ff5e',
          'on-primary': '#080810',
          secondary: '#585880',
          error: '#ff6b6b',
          warning: '#ffc857',
          info: '#60a5fa',
          success: '#4ade80',
        },
      },
    },
  },
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(vuetify)
app.mount('#app')
