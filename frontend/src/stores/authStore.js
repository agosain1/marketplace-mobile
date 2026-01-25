import { defineStore } from 'pinia'
import { api } from 'src/boot/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: true
  }),

  getters: {
    currentUser: (state) => state.user,
    isLoggedIn: (state) => state.isAuthenticated && !!state.user,
    userFullName: (state) => {
      if (!state.user) return ''
      return `${state.user.fname || ''} ${state.user.lname || ''}`.trim()
    }
  },

  actions: {
    // Fetch current user from token validation
    async fetchMe() {
      try {
        console.log('Fetching user data...')
        const response = await api.get('/auth/me')
        console.log('User data fetched:', response.data)

        this.user = response.data
        this.isAuthenticated = true
        this.isLoading = false
      } catch (error) {
        console.error('Failed to fetch user:', error)
        this.user = null
        this.isAuthenticated = false
        this.isLoading = false
      }
    },

    // Logout user
    async logout() {
      try {
        await api.post('/auth/logout')
      } finally {
        this.user = null
        this.isAuthenticated = false
        this.isLoading = false
      }
    },

    // Set authenticated user (for login/register)
    setAuth(userData) {
      this.user = userData
      this.isAuthenticated = true
      this.isLoading = false
    },

    // Clear auth data
    clearAuth() {
      this.user = null
      this.isAuthenticated = false
      this.isLoading = false
    }
  }
})
