import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLoadingStore = defineStore('loading', () => {
  const loading = ref(false)
  const activeRequests = ref(0)

  function start() {
    activeRequests.value++
    loading.value = true
  }

  function stop() {
    activeRequests.value = Math.max(0, activeRequests.value - 1)
    if (activeRequests.value === 0) {
      loading.value = false
    }
  }

  return { loading, start, stop }
})
