import { api } from 'src/boot/axios'

// Configure axios to always include credentials (cookies)
api.defaults.withCredentials = true

export const authService = {
  // Validate current token via cookie
  async validateToken() {
    return await api.get('/auth/validate-token')
  }
}

export default api
