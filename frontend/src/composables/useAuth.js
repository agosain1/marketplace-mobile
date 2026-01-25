import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'stores/authStore.js'

export function useAuth() {
  const router = useRouter()
  const authStore = useAuthStore()

  // Fetch user data from backend
  const fetchMe = async () => {
    await authStore.fetchMe()
    return authStore.isAuthenticated
  }

  // Validate token (alias for fetchMe for backward compatibility)
  const validateToken = async () => {
    return await fetchMe()
  }

  // Require authentication (for protected routes)
  const requireAuth = async () => {
    if (!authStore.isAuthenticated) {
      const isValid = await validateToken()
      if (!isValid) {
        router.push('/login')
        return false
      }
    }
    return true
  }

  // Start periodic token validation (every 5 minutes)
  const startTokenValidation = () => {
    // Initial validation
    fetchMe()

    // Periodic validation
    setInterval(async () => {
      if (authStore.isAuthenticated) {
        await fetchMe()
      }
    }, 5 * 60 * 1000) // 5 minutes
  }

  // Logout
  const logout = async () => {
    await authStore.logout()
    router.push('/login')
  }

  return {
    // State (from store)
    isAuthenticated: computed(() => authStore.isLoggedIn),
    user: computed(() => authStore.currentUser),
    isLoading: computed(() => authStore.isLoading),

    // Methods
    fetchMe,
    validateToken, // Keep for backward compatibility
    requireAuth,
    startTokenValidation,
    logout
  }
}
