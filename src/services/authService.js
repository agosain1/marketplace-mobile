import { api } from 'src/boot/axios'

// Configure axios to always include credentials (cookies)
api.defaults.withCredentials = true

export const authService = {
  // Validate current token via cookie
  async validateToken() {
    try {
      const response = await api.get('/auth/validate-token')
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Token validation failed'
      }
    }
  },

  // Login user
  async login(email, password) {
    try {
       const response = await api.post(`auth/login`, {
          email: email,
          password: password
        })
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      }
    }
  },

  // Logout user
  async logout() {
    try {
      await api.post(`auth/logout`)
      return {
        success: true
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Logout failed'
      }
    }
  },

  // Register user
  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed'
      }
    }
  },

  // Verify email
  async verifyEmail(email, code) {
    try {
      const response = await api.post('/auth/verify-email', { email, code })
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Email verification failed'
      }
    }
  },

  // Resend verification code
  async resendVerification(email) {
    try {
      const response = await api.post('/auth/resend-verification', { email })
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to resend verification'
      }
    }
  }
}

export default api
