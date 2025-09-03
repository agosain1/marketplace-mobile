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
    },

    // Login action
    async login(email, password) {
      this.isLoading = true
      try {
        const result = await authService.login(email, password)

        if (result.success) {
          this.setAuth(result.data.user)
          return { success: true, data: result.data }
        } else {
          return { success: false, error: result.error }
        }
      } catch (error) {
        return { success: false, error: 'Login failed. Please try again.' + error }
      } finally {
        this.isLoading = false
      }
    },

    // Logout action
    async logout() {
      try {
        await authService.logout()
      } catch (error) {
        console.error('Logout request failed:', error)
      } finally {
        // Clear auth state regardless of API call result
        this.clearAuth()
      }
    },

    // Update user data
    updateUser(userData) {
      this.user = { ...this.user, ...userData }
    }
  }
})
