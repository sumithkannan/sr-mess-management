import axios from 'axios'
import router from '../router'
import { useLoadingStore } from '../stores/loading'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  
  if (config.method?.toUpperCase() === 'POST') {
    try {
      const loadingStore = useLoadingStore()
      loadingStore.start()
    } catch (e) {
      // ignore if store not ready
    }
  }
  return config
})

api.interceptors.response.use(
  response => {
    if (response.config?.method?.toUpperCase() === 'POST') {
      try {
        const loadingStore = useLoadingStore()
        loadingStore.stop()
      } catch (e) {
        // ignore
      }
    }
    return response
  },
  error => {
    if (error.config?.method?.toUpperCase() === 'POST') {
      try {
        const loadingStore = useLoadingStore()
        loadingStore.stop()
      } catch (e) {
        // ignore
      }
    }
    console.error('[API Error]', error.config?.url,
      error.response?.status,
      error.response?.data?.detail || error.message)
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default api
