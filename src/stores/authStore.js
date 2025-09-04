import { defineStore } from 'pinia'
import { authService } from '../services/authService'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: false
  }),

  getters: {
    currentUser: (state) => state.user,
    isLoggedIn: (state) => state.isAuthenticated && !!state.user,
    userFullName: (state) => {
      if (!state.user) return ''
      return `${state.user.firstName || ''} ${state.user.lastName || ''}`.trim()
    }
  },

  actions: {
    // Set authenticated user (from cookie validation)
    setAuth(userData) {
      this.user = userData
      this.isAuthenticated = true
    },

    // Clear auth data
    clearAuth() {
      this.user = null
      this.isAuthenticated = false
    },

    // Validate current token (cookies are sent automatically)
    async validateToken() {
      this.isLoading = true
      try {
        const result = await authService.validateToken()

        if (result.success) {
          this.setAuth(result.data.user)
          return true
        } else {
          this.clearAuth()
          return false
        }
      } catch (error) {
        console.error('Token validation failed:', error)
        this.clearAuth()
        return false
      } finally {
        this.isLoading = false
      }
    }
  }
})
