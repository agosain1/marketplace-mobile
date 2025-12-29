import { boot } from 'quasar/wrappers'
import { wsService } from 'src/services/websocketService'
import { useAuthStore } from 'stores/authStore'
import { useMessagesStore } from 'stores/messagesStore'

/**
 * WebSocket Boot File
 *
 * Initializes WebSocket connection when the app starts (if user is authenticated)
 * Sets up message store listeners for real-time updates
 */
export default boot(({ app }) => {
  const authStore = useAuthStore()
  const messagesStore = useMessagesStore()

  // Initialize message store WebSocket listeners
  messagesStore.initWebSocket()

  // Connect WebSocket if user is already authenticated
  if (authStore.isLoggedIn) {
    console.log('🔌 User is authenticated, connecting WebSocket...')

    // Set current user in messages store
    if (authStore.user?.id) {
      messagesStore.setCurrentUser(authStore.user.id)
    }

    // Connect to WebSocket
    wsService.connect()
  } else {
    console.log('⏸️ User not authenticated, WebSocket connection delayed')
  }

  // Watch for auth changes to connect/disconnect WebSocket
  authStore.$subscribe((mutation, state) => {
    if (state.isAuthenticated && state.user) {
      // User just logged in
      console.log('✅ User logged in, connecting WebSocket...')

      // Set current user in messages store
      if (state.user.id) {
        messagesStore.setCurrentUser(state.user.id)
      }

      // Connect WebSocket
      if (!wsService.isConnected) {
        wsService.connect()
      }
    } else {
      // User logged out
      console.log('👋 User logged out, disconnecting WebSocket...')

      // Disconnect WebSocket permanently (until next login)
      wsService.disconnect(true)

      // Clear message store state
      messagesStore.clearState()
    }
  })

  // Make WebSocket service globally available (optional)
  app.config.globalProperties.$ws = wsService

  // Handle app visibility changes (reconnect when app becomes visible)
  if (typeof document !== 'undefined') {
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && authStore.isLoggedIn) {
        // App became visible and user is logged in
        if (!wsService.isConnected) {
          console.log('👀 App visible, reconnecting WebSocket...')
          wsService.shouldReconnect = true
          wsService.connect()
        }
      }
    })
  }

  console.log('🚀 WebSocket boot file loaded')
})