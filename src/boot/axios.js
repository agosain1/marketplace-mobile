import { defineBoot } from '#q-app/wrappers'
import axios from 'axios'
import { useAuthStore } from 'src/stores/authStore.js'

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
// Ensure baseURL always has a trailing slash
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const baseURL = apiUrl.endsWith('/') ? apiUrl : `${apiUrl}/`

const api = axios.create({
  baseURL: baseURL
})

// Add response interceptor to handle 401 errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth store on 401 Unauthorized
      const authStore = useAuthStore()
      authStore.clearAuth()
      console.log('401 detected - cleared auth store')
    }
    return Promise.reject(error)
  }
)

export default defineBoot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
})

export { api }
