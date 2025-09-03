import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Notify } from 'quasar'

export function useAuth() {
  const router = useRouter()
  const authStore = useAuthStore()

  // Validate token with backend
  const validateToken = async () => {
    return await authStore.validateToken()
  }

  // Login function
  const login = async (email, password) => {
    const result = await authStore.login(email, password)
    
    if (result.success) {
      Notify.create({
        type: 'positive',
        message: 'Login successful!',
        position: 'top'
      })
    } else {
      Notify.create({
        type: 'negative',
        message: result.error,
        position: 'top'
      })
    }
    
    return result
  }

  // Logout function
  const logout = async (showMessage = true) => {
    await authStore.logout()
    
    if (showMessage) {
      Notify.create({
        type: 'info',
        message: 'You have been logged out',
        position: 'top'
      })
    }
    
    // Redirect to login page if not already there
    if (router.currentRoute.value.path !== '/login' && router.currentRoute.value.path !== '/') {
      router.push('/login')
    }
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
    }, 5 * 60 * 1000) // 5 minutes
  }

  return {
    // State (from store)
    isAuthenticated: computed(() => authStore.isLoggedIn),
    user: computed(() => authStore.currentUser),
    isLoading: computed(() => authStore.isLoading),
    
    // Methods
    validateToken,
    login,
    logout,
    requireAuth,
    startTokenValidation
  }
}