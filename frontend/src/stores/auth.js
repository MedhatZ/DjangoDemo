import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('poc_token') || '',
    user: JSON.parse(localStorage.getItem('poc_user') || 'null')
  }),
  getters: {
    isAuthenticated: (s) => Boolean(s.token)
  },
  actions: {
    async login(username, password) {
      const { data } = await api.post('/api/auth/login/', { username, password })
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem('poc_token', this.token)
      localStorage.setItem('poc_user', JSON.stringify(this.user))
      return data
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('poc_token')
      localStorage.removeItem('poc_user')
    }
  }
})
