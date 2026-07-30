import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)

app.config.errorHandler = (err, instance, info) => {
  console.error('[Vue Error]', err, info)
}

window.onerror = (msg, source, line, col, error) => {
  console.error('[Window Error]', msg, error?.stack || error)
}

window.addEventListener('unhandledrejection', event => {
  console.error('[Unhandled Promise]', event.reason?.stack || event.reason)
})

app.mount('#app')
