import { defineStore } from 'pinia'
import { wsService } from 'src/services/websocketService'
import { api } from 'src/boot/axios'

/**
 * Messages Store - Manages real-time messaging state
 *
 * Primary mode: WebSocket for all live operations
 * Fallback mode: REST API when WebSocket disconnected
 */
export const useMessagesStore = defineStore('messages', {
  state: () => ({
    // Connection state
    isConnected: false,

    // Conversations and messages
    conversations: [],
    currentMessages: [],
    selectedConversation: null,
    selectedConversationName: null,
    selectedConversationId: null, // For typing indicators

    // Real-time features
    typingUsers: {}, // { userId: true/false }
    onlineUsers: new Set(), // Set of online user IDs

    // Unread counts
    unreadCount: 0,

    // Current user
    currentUserId: null
  }),

  getters: {
    /**
     * Check if a user is online
     */
    isUserOnline: (state) => (userId) => {
      return state.onlineUsers.has(userId)
    },

    /**
     * Check if a user is typing
     */
    isUserTyping: (state) => (userId) => {
      return state.typingUsers[userId] === true
    },

    /**
     * Get total unread count across all conversations
     */
    totalUnreadCount: (state) => {
      return state.conversations.reduce((sum, conv) => sum + (conv.unread_count || 0), 0)
    },

    /**
     * Get conversation by email
     */
    getConversationByEmail: (state) => (email) => {
      return state.conversations.find(conv => conv.other_user_email === email)
    }
  },

  actions: {
    /**
     * Initialize WebSocket listeners
     * Should be called once when the app starts
     */
    initWebSocket() {
      console.log('🔌 Initializing WebSocket listeners')

      // Connection events
      wsService.on('connected', () => {
        console.log('✅ WebSocket connected in store')
        this.isConnected = true

        // Request initial unread count
        wsService.getUnreadCount()
      })

      wsService.on('disconnected', () => {
        console.log('❌ WebSocket disconnected in store')
        this.isConnected = false
      })

      wsService.on('error', (error) => {
        console.error('WebSocket error in store:', error)
      })

      // Message events
      wsService.on('message_received', (data) => {
        this.handleMessageReceived(data)
      })

      wsService.on('message_sent', (data) => {
        this.handleMessageSent(data)
      })

      wsService.on('read_receipt', (data) => {
        this.handleReadReceipt(data)
      })

      // Typing indicators
      wsService.on('typing_indicator', (data) => {
        this.handleTypingIndicator(data)
      })

      // User status
      wsService.on('user_status', (data) => {
        this.handleUserStatus(data)
      })

      // Unread count updates
      wsService.on('unread_count_update', (data) => {
        this.handleUnreadCountUpdate(data)
      })

      // Send failed (WebSocket not connected)
      wsService.on('send_failed', (data) => {
        console.warn('⚠️ WebSocket send failed, message not sent:', data)
        // Could show a notification to user here
      })
    },

    /**
     * Handle incoming message from another user
     */
    handleMessageReceived(message) {
      console.log('📨 Message received:', message)

      // If viewing this conversation, add message to current view
      if (this.selectedConversation === message.sender_email) {
        this.currentMessages.push(message)

        // Mark as read immediately via WebSocket
        if (wsService.isConnected) {
          wsService.markAsRead(message.message_id)
        } else {
          // Fallback to REST API
          this.markAsReadREST(message.message_id)
        }
      }

      // Update conversations list
      this.loadConversations()

      // Trigger unread count update (if not in this conversation)
      if (this.selectedConversation !== message.sender_email) {
        wsService.getUnreadCount()
      }
    },

    /**
     * Handle confirmation of sent message
     */
    handleMessageSent(message) {
      console.log('✅ Message sent confirmation:', message)

      // Add to current messages if not already there
      const exists = this.currentMessages.find(m => m.message_id === message.message_id)
      if (!exists) {
        this.currentMessages.push(message)
      }

      // Update conversations list
      this.loadConversations()
    },

    /**
     * Handle read receipt for sent message
     */
    handleReadReceipt(data) {
      console.log('👁️ Read receipt:', data)

      // Update message in current view
      const message = this.currentMessages.find(m => m.message_id === data.message_id)
      if (message) {
        message.read_at = data.read_at
      }

      // Could also update in conversations list
      this.loadConversations()
    },

    /**
     * Handle typing indicator
     */
    handleTypingIndicator(data) {
      const { user_id, typing } = data

      if (typing) {
        this.typingUsers[user_id] = true

        // Auto-clear after 3 seconds (in case stop event is missed)
        setTimeout(() => {
          this.typingUsers[user_id] = false
        }, 3000)
      } else {
        this.typingUsers[user_id] = false
      }
    },

    /**
     * Handle user online/offline status
     */
    handleUserStatus(data) {
      const { user_id, status } = data

      if (status === 'online') {
        this.onlineUsers.add(user_id)
      } else {
        this.onlineUsers.delete(user_id)
      }
    },

    /**
     * Handle unread count update
     */
    handleUnreadCountUpdate(data) {
      console.log('📬 Unread count update:', data)
      this.unreadCount = data.unread_count
    },

    /**
     * Send a message (WebSocket primary, REST fallback)
     */
    async sendMessage(receiverEmail, content) {
      if (!content || !content.trim()) {
        console.warn('Cannot send empty message')
        return false
      }

      // Try WebSocket first
      if (wsService.isConnected) {
        const success = wsService.sendMessage(receiverEmail, content)
        if (success) {
          console.log('📤 Message sent via WebSocket')
          return true
        }
      }

      // Fallback to REST API
      console.log('📤 Sending message via REST API (fallback)')
      return await this.sendMessageREST(receiverEmail, content)
    },

    /**
     * Send message via REST API (fallback)
     */
    async sendMessageREST(receiverEmail, content) {
      try {
        const response = await api.post('/messages/send', {
          receiver_email: receiverEmail,
          content: content
        })

        const sentMessage = response.data

        // Add to current messages
        this.currentMessages.push(sentMessage)

        // Update conversations list
        await this.loadConversations()

        return true
      } catch (error) {
        console.error('Error sending message via REST:', error)
        return false
      }
    },

    /**
     * Mark message as read via REST API (fallback)
     */
    async markAsReadREST(messageId) {
      try {
        await api.patch(`/messages/${messageId}/read`)
      } catch (error) {
        console.error('Error marking message as read via REST:', error)
      }
    },

    /**
     * Start typing indicator
     */
    startTyping(receiverId) {
      if (wsService.isConnected && receiverId) {
        wsService.startTyping(receiverId)
      }
    },

    /**
     * Stop typing indicator
     */
    stopTyping(receiverId) {
      if (wsService.isConnected && receiverId) {
        wsService.stopTyping(receiverId)
      }
    },

    /**
     * Load conversations from REST API
     */
    async loadConversations() {
      try {
        const response = await api.get('/messages/user-messages')
        const messages = response.data

        // Group messages by conversation partner
        const conversationMap = new Map()

        messages.forEach(message => {
          const otherUserEmail = message.sender_id === this.currentUserId
            ? message.receiver_email
            : message.sender_email

          const otherUserName = message.sender_id === this.currentUserId
            ? message.receiver_name
            : message.sender_name

          const otherUserId = message.sender_id === this.currentUserId
            ? message.receiver_id
            : message.sender_id

          if (!conversationMap.has(otherUserEmail)) {
            conversationMap.set(otherUserEmail, {
              other_user_email: otherUserEmail,
              other_user_name: otherUserName,
              other_user_id: otherUserId,
              last_message: message.content,
              last_message_time: message.created_at,
              unread_count: 0
            })
          }

          const conv = conversationMap.get(otherUserEmail)

          // Update to most recent message
          if (new Date(message.created_at) > new Date(conv.last_message_time)) {
            conv.last_message = message.content
            conv.last_message_time = message.created_at
          }

          // Count unread messages
          if (!message.read_at && message.receiver_id === this.currentUserId) {
            conv.unread_count++
          }
        })

        this.conversations = Array.from(conversationMap.values())
          .sort((a, b) => new Date(b.last_message_time) - new Date(a.last_message_time))

      } catch (error) {
        console.error('Error loading conversations:', error)
      }
    },

    /**
     * Load a specific conversation
     */
    async loadConversation(email) {
      try {
        const response = await api.get(`/messages/conversation/${email}`)
        this.currentMessages = response.data

        // Mark unread messages as read
        const unreadMessages = this.currentMessages.filter(
          msg => !msg.read_at && msg.receiver_id === this.currentUserId
        )

        for (const message of unreadMessages) {
          if (wsService.isConnected) {
            wsService.markAsRead(message.message_id)
          } else {
            await this.markAsReadREST(message.message_id)
          }
        }

        // Update unread count
        if (wsService.isConnected) {
          wsService.getUnreadCount()
        }

      } catch (error) {
        console.error('Error loading conversation:', error)
      }
    },

    /**
     * Select a conversation
     */
    async selectConversation(email) {
      this.selectedConversation = email

      // Find conversation details
      const conversation = this.conversations.find(conv => conv.other_user_email === email)
      if (conversation) {
        this.selectedConversationName = conversation.other_user_name || conversation.other_user_email
        this.selectedConversationId = conversation.other_user_id
      }

      // Load messages
      await this.loadConversation(email)
    },

    /**
     * Set current user ID
     */
    setCurrentUser(userId) {
      this.currentUserId = userId
    },

    /**
     * Clear all state (on logout)
     */
    clearState() {
      this.conversations = []
      this.currentMessages = []
      this.selectedConversation = null
      this.selectedConversationName = null
      this.selectedConversationId = null
      this.typingUsers = {}
      this.onlineUsers = new Set()
      this.unreadCount = 0
      this.currentUserId = null
      this.isConnected = false
    }
  }
})