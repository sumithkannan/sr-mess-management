import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || null
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin'
  },
  actions: {
    async login(username, password) {
      const { data } = await api.post('/api/auth/login', { username, password })
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      return data
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
    async fetchUser() {
      try {
        const { data } = await api.get('/api/auth/me')
        this.user = data
        localStorage.setItem('user', JSON.stringify(data))
      } catch {
        this.logout()
      }
    }
  }
})
