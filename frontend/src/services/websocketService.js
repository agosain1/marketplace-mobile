/**
 * WebSocket Service for Real-time Messaging
 *
 * Handles WebSocket connection to the backend for live chat functionality.
 * Features:
 * - Automatic reconnection with exponential backoff
 * - Event-based message handling
 * - Automatic cookie-based authentication
 * - Connection state management
 */

class WebSocketService {
  constructor() {
    this.ws = null
    this.isConnected = false
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 10
    this.reconnectDelay = 1000 // Start with 1 second
    this.listeners = {}
    this.reconnectTimeout = null
    this.shouldReconnect = true
  }

  /**
   * Connect to WebSocket server
   * Uses existing auth_token cookie for authentication
   */
  connect() {
    // Prevent multiple simultaneous connections
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      console.log('WebSocket already connected or connecting')
      return
    }

    try {
      // Get WebSocket URL from environment or use default
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

      // Determine protocol (ws or wss)
      const protocol = apiUrl.startsWith('https') ? 'wss' : 'ws'
      const baseUrl = apiUrl.replace(/^https?:\/\//, '').replace(/\/$/, '')

      const wsUrl = `${protocol}://${baseUrl}/ws/messages`

      console.log('Connecting to WebSocket:', wsUrl)

      // Create WebSocket connection (cookies are sent automatically)
      this.ws = new WebSocket(wsUrl)

      // Connection opened
      this.ws.onopen = () => {
        console.log('✅ WebSocket connected')
        this.isConnected = true
        this.reconnectAttempts = 0
        this._emit('connected')
      }

      // Listen for messages
      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          console.log('📨 WebSocket message received:', message.type, message.data)

          // Emit event to listeners
          this._emit(message.type, message.data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      // Connection closed
      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        this.isConnected = false
        this._emit('disconnected')

        // Attempt to reconnect if not manually closed
        if (this.shouldReconnect) {
          this._attemptReconnect()
        }
      }

      // Connection error
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this._emit('error', error)
      }

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      this._emit('error', error)
    }
  }

  /**
   * Disconnect from WebSocket server
   * @param {boolean} permanent - If true, won't auto-reconnect
   */
  disconnect(permanent = false) {
    if (permanent) {
      this.shouldReconnect = false
    }

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }

    if (this.ws) {
      this.ws.close()
      this.ws = null
      this.isConnected = false
    }
  }

  /**
   * Send a message through WebSocket
   * @param {string} type - Message type
   * @param {object} data - Message data
   */
  send(type, data = {}) {
    if (this.ws && this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      const message = { type, data }
      console.log('📤 Sending WebSocket message:', type, data)
      this.ws.send(JSON.stringify(message))
      return true
    } else {
      console.warn('⚠️ WebSocket not connected, cannot send message')
      this._emit('send_failed', { type, data })
      return false
    }
  }

  /**
   * Send a chat message
   * @param {string} receiverEmail - Email of the recipient
   * @param {string} content - Message content
   * @returns {boolean} - True if sent, false if failed
   */
  sendMessage(receiverEmail, content) {
    return this.send('send_message', {
      receiver_email: receiverEmail,
      content: content
    })
  }

  /**
   * Mark a message as read
   * @param {string} messageId - UUID of the message
   * @returns {boolean} - True if sent, false if failed
   */
  markAsRead(messageId) {
    return this.send('mark_read', {
      message_id: messageId
    })
  }

  /**
   * Notify that user started typing
   * @param {string} receiverId - UUID of the recipient
   * @returns {boolean} - True if sent, false if failed
   */
  startTyping(receiverId) {
    return this.send('typing_start', {
      receiver_id: receiverId
    })
  }

  /**
   * Notify that user stopped typing
   * @param {string} receiverId - UUID of the recipient
   * @returns {boolean} - True if sent, false if failed
   */
  stopTyping(receiverId) {
    return this.send('typing_stop', {
      receiver_id: receiverId
    })
  }

  /**
   * Request unread message count
   * @returns {boolean} - True if sent, false if failed
   */
  getUnreadCount() {
    return this.send('get_unread_count', {})
  }

  /**
   * Register an event listener
   * @param {string} event - Event name
   * @param {function} callback - Callback function
   */
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = []
    }
    this.listeners[event].push(callback)
  }

  /**
   * Unregister an event listener
   * @param {string} event - Event name
   * @param {function} callback - Callback function to remove
   */
  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback)
    }
  }

  /**
   * Remove all listeners for an event
   * @param {string} event - Event name
   */
  removeAllListeners(event) {
    if (event) {
      delete this.listeners[event]
    } else {
      this.listeners = {}
    }
  }

  /**
   * Emit an event to all registered listeners
   * @private
   */
  _emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in ${event} listener:`, error)
        }
      })
    }
  }

  /**
   * Attempt to reconnect with exponential backoff
   * @private
   */
  _attemptReconnect() {
    if (!this.shouldReconnect) {
      return
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Max reconnection attempts reached')
      this._emit('max_reconnect_attempts')
      return
    }

    this.reconnectAttempts++

    // Exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s (max)
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      32000
    )

    console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    this.reconnectTimeout = setTimeout(() => {
      this.connect()
    }, delay)
  }

  /**
   * Get current connection state
   * @returns {object} - Connection state info
   */
  getState() {
    return {
      isConnected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      readyState: this.ws ? this.ws.readyState : WebSocket.CLOSED
    }
  }
}

// Create and export singleton instance
export const wsService = new WebSocketService()
export default wsService