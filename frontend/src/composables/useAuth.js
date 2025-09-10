import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'stores/authStore.js'

export function useAuth() {
  const router = useRouter()
  const authStore = useAuthStore()

  // Validate token with backend
  const validateToken = async () => {
    return await authStore.validateToken()
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
    validateToken()

    // Periodic validation
    setInterval(async () => {
      if (authStore.isAuthenticated) {
        await validateToken()
      }
    }, 5 * 60 * 1000) // 5 minutes = 5 * 60 * 1000
  }

  return {
    // State (from store)
    isAuthenticated: computed(() => authStore.isLoggedIn),
    user: computed(() => authStore.currentUser),
    isLoading: computed(() => authStore.isLoading),

    // Methods
    validateToken,
    requireAuth,
    startTokenValidation
  }
}
