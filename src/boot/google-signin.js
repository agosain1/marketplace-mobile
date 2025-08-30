import { defineBoot } from '#q-app/wrappers'
import { googleAuthConfig } from '../config/google.js'

export default defineBoot(async ({ app }) => {
  try {
    // Load Google Identity Services script
    if (!window.google) {
      await new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://accounts.google.com/gsi/client'
        script.onload = resolve
        script.onerror = reject
        document.head.appendChild(script)
      })
    }

    // Wait a bit for Google script to initialize
    await new Promise(resolve => setTimeout(resolve, 100))

    // Initialize Google Identity Services
    if (window.google?.accounts?.id) {
      window.google.accounts.id.initialize({
        client_id: googleAuthConfig.clientId,
        auto_select: false,
        cancel_on_tap_outside: true,
      })
    }

    // Make client ID available globally for components
    app.config.globalProperties.$googleClientId = googleAuthConfig.clientId
  } catch (error) {
    console.error('Failed to initialize Google Sign-In:', error)
  }
})
