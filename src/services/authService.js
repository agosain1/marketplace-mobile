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
        error: error.response?.data || error.message
      }
    }
  }
}

export default api
