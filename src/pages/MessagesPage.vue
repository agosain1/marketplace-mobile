<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="arrow_back" @click="goHome" />
        <q-toolbar-title>Messages</q-toolbar-title>
        <q-btn flat dense round icon="refresh" @click="refreshMessages" />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="flex">
        <div class="row full-width">
          <!-- Conversations List -->
          <div class="col-12 col-md-4">
            <q-list bordered separator class="full-height">
              <q-item-label header>Conversations</q-item-label>
              
              <q-item
                v-for="conversation in conversations"
                :key="conversation.other_user_email"
                clickable
                v-ripple
                :active="selectedConversation === conversation.other_user_email"
                @click="selectConversation(conversation.other_user_email)"
                class="q-pa-md"
              >
                <q-item-section avatar>
                  <q-avatar color="primary" text-color="white" size="40px">
                    {{ conversation.other_user_email.charAt(0).toUpperCase() }}
                  </q-avatar>
                </q-item-section>
                
                <q-item-section>
                  <q-item-label class="text-weight-medium">
                    {{ conversation.other_user_email }}
                  </q-item-label>
                  <q-item-label caption lines="1">
                    {{ conversation.last_message }}
                  </q-item-label>
                </q-item-section>
                
                <q-item-section side>
                  <div class="column items-end">
                    <q-item-label caption>
                      {{ formatTime(conversation.last_message_time) }}
                    </q-item-label>
                    <q-badge
                      v-if="conversation.unread_count > 0"
                      color="red"
                      rounded
                      :label="conversation.unread_count"
                      class="q-mt-xs"
                    />
                  </div>
                </q-item-section>
              </q-item>
              
              <q-separator />
              
              <!-- New Message Button -->
              <q-item clickable v-ripple @click="showNewMessageDialog = true">
                <q-item-section avatar>
                  <q-icon name="add" color="primary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>New Message</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <!-- Messages View -->
          <div class="col-12 col-md-8">
            <div v-if="!selectedConversation" class="flex flex-center full-height">
              <div class="text-center">
                <q-icon name="message" size="80px" color="grey-5" />
                <div class="text-h6 text-grey-6 q-mt-md">Select a conversation to start messaging</div>
              </div>
            </div>
            
            <div v-else class="column full-height">
              <!-- Chat Header -->
              <q-toolbar class="bg-grey-1">
                <q-avatar color="primary" text-color="white" size="32px">
                  {{ selectedConversation.charAt(0).toUpperCase() }}
                </q-avatar>
                <q-toolbar-title class="q-ml-sm">{{ selectedConversation }}</q-toolbar-title>
              </q-toolbar>
              
              <!-- Messages Container -->
              <q-scroll-area
                ref="messagesScrollArea"
                class="col"
                style="height: calc(100vh - 200px);"
              >
                <div class="q-pa-md">
                  <div
                    v-for="message in currentMessages"
                    :key="message.message_id"
                    class="q-mb-md"
                  >
                    <div
                      :class="[
                        'message-bubble',
                        message.sender_id === currentUserId ? 'sent' : 'received'
                      ]"
                    >
                      <div class="message-content">{{ message.content }}</div>
                      <div class="message-time">
                        {{ formatTime(message.created_at) }}
                        <q-icon
                          v-if="message.sender_id === currentUserId"
                          :name="message.read_at ? 'done_all' : 'done'"
                          :color="message.read_at ? 'blue' : 'grey'"
                          size="12px"
                          class="q-ml-xs"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </q-scroll-area>
              
              <!-- Message Input -->
              <q-toolbar class="bg-white">
                <q-input
                  v-model="newMessage"
                  placeholder="Type a message..."
                  outlined
                  dense
                  class="col"
                  @keyup.enter="sendMessage"
                  :loading="sendingMessage"
                />
                <q-btn
                  round
                  dense
                  color="primary"
                  icon="send"
                  class="q-ml-sm"
                  @click="sendMessage"
                  :loading="sendingMessage"
                  :disable="!newMessage.trim()"
                />
              </q-toolbar>
            </div>
          </div>
        </div>
      </q-page>
    </q-page-container>

    <!-- New Message Dialog -->
    <q-dialog v-model="showNewMessageDialog">
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">New Message</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="newMessageEmail"
            label="Recipient Email"
            outlined
            dense
          />
          <q-input
            v-model="newMessageContent"
            label="Message"
            type="textarea"
            outlined
            dense
            class="q-mt-md"
          />
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            flat
            label="Send"
            @click="sendNewMessage"
            :loading="sendingMessage"
            :disable="!newMessageEmail.trim() || !newMessageContent.trim()"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'src/boot/axios'
import { useQuasar } from 'quasar'

const router = useRouter()
const $q = useQuasar()

// Reactive data
const conversations = ref([])
const selectedConversation = ref(null)
const currentMessages = ref([])
const newMessage = ref('')
const sendingMessage = ref(false)
const currentUserId = ref(null)
const showNewMessageDialog = ref(false)
const newMessageEmail = ref('')
const newMessageContent = ref('')
const messagesScrollArea = ref(null)

// Methods
const goHome = () => {
  router.push('/')
}

const refreshMessages = async () => {
  await loadConversations()
  if (selectedConversation.value) {
    await loadConversation(selectedConversation.value)
  }
}

const loadConversations = async () => {
  try {
    // Get user messages and group them by conversation
    const token = localStorage.getItem('auth_token')
    if (!token) {
      router.push('/login')
      return
    }
    
    const response = await api.get('/messages/user-messages', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    const messages = response.data
    
    // Group messages by conversation partner
    const conversationMap = new Map()
    
    messages.forEach(message => {
      const otherUserEmail = message.sender_id === currentUserId.value 
        ? message.receiver_email 
        : message.sender_email
      
      if (!conversationMap.has(otherUserEmail)) {
        conversationMap.set(otherUserEmail, {
          other_user_email: otherUserEmail,
          last_message: message.content,
          last_message_time: message.created_at,
          unread_count: 0
        })
      }
      
      const conv = conversationMap.get(otherUserEmail)
      if (new Date(message.created_at) > new Date(conv.last_message_time)) {
        conv.last_message = message.content
        conv.last_message_time = message.created_at
      }
      
      if (!message.read_at && message.receiver_id === currentUserId.value) {
        conv.unread_count++
      }
    })
    
    conversations.value = Array.from(conversationMap.values())
      .sort((a, b) => new Date(b.last_message_time) - new Date(a.last_message_time))
    
  } catch (error) {
    console.error('Error loading conversations:', error)
    $q.notify({
      color: 'negative',
      message: 'Failed to load conversations'
    })
  }
}

const selectConversation = async (email) => {
  selectedConversation.value = email
  await loadConversation(email)
}

const loadConversation = async (email) => {
  try {
    const token = localStorage.getItem('auth_token')
    const response = await api.get(`/messages/conversation/${email}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    currentMessages.value = response.data
    
    // Mark messages as read
    const unreadMessages = currentMessages.value.filter(
      msg => !msg.read_at && msg.receiver_id === currentUserId.value
    )
    
    for (const message of unreadMessages) {
      try {
        await api.patch(`/messages/${message.message_id}/read`, {}, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      } catch (error) {
        console.error('Error marking message as read:', error)
      }
    }
    
    // Trigger unread count update on other pages
    if (unreadMessages.length > 0) {
      localStorage.setItem('messages_updated', Date.now().toString())
    }
    
    // Scroll to bottom
    await nextTick()
    if (messagesScrollArea.value) {
      messagesScrollArea.value.setScrollPercentage('vertical', 1)
    }
    
  } catch (error) {
    console.error('Error loading conversation:', error)
    $q.notify({
      color: 'negative',
      message: 'Failed to load conversation'
    })
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || !selectedConversation.value || sendingMessage.value) return
  
  sendingMessage.value = true
  
  try {
    const token = localStorage.getItem('auth_token')
    const response = await api.post('/messages/send', {
      receiver_email: selectedConversation.value,
      content: newMessage.value.trim()
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    const sentMessage = response.data
    currentMessages.value.push(sentMessage)
    newMessage.value = ''
    
    // Scroll to bottom
    await nextTick()
    if (messagesScrollArea.value) {
      messagesScrollArea.value.setScrollPercentage('vertical', 1)
    }
    
    // Update conversations list
    await loadConversations()
    
  } catch (error) {
    console.error('Error sending message:', error)
    $q.notify({
      color: 'negative',
      message: 'Failed to send message'
    })
  } finally {
    sendingMessage.value = false
  }
}

const sendNewMessage = async () => {
  if (!newMessageEmail.value.trim() || !newMessageContent.value.trim() || sendingMessage.value) return
  
  sendingMessage.value = true
  
  try {
    const token = localStorage.getItem('auth_token')
    await api.post('/messages/send', {
      receiver_email: newMessageEmail.value.trim(),
      content: newMessageContent.value.trim()
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    const recipientEmail = newMessageEmail.value.trim()
    
    showNewMessageDialog.value = false
    newMessageEmail.value = ''
    newMessageContent.value = ''
    
    // Select the new conversation
    selectedConversation.value = recipientEmail
    await loadConversations()
    await loadConversation(recipientEmail)
    
    $q.notify({
      color: 'positive',
      message: 'Message sent successfully'
    })
    
  } catch (error) {
    console.error('Error sending new message:', error)
    $q.notify({
      color: 'negative',
      message: 'Failed to send message'
    })
  } finally {
    sendingMessage.value = false
  }
}

const formatTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = (now - date) / (1000 * 60 * 60)
  
  if (diffInHours < 24) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } else if (diffInHours < 24 * 7) {
    return date.toLocaleDateString([], { weekday: 'short' })
  } else {
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
  }
}

// Load data on mount
onMounted(async () => {
  // Get current user ID from token
  const token = localStorage.getItem('auth_token')
  if (!token) {
    router.push('/login')
    return
  }
  
  try {
    // Decode JWT to get user ID (simplified - in production use a proper JWT library)
    const payload = JSON.parse(atob(token.split('.')[1]))
    currentUserId.value = payload.uuid
  } catch (error) {
    console.error('Error parsing token:', error)
    router.push('/login')
    return
  }
  
  await loadConversations()
})
</script>

<style scoped>
.message-bubble {
  max-width: 70%;
  padding: 8px 12px;
  border-radius: 12px;
  margin-bottom: 4px;
}

.message-bubble.sent {
  background-color: #1976d2;
  color: white;
  margin-left: auto;
  border-bottom-right-radius: 4px;
}

.message-bubble.received {
  background-color: #f5f5f5;
  color: #333;
  margin-right: auto;
  border-bottom-left-radius: 4px;
}

.message-content {
  word-wrap: break-word;
  margin-bottom: 4px;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
  text-align: right;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.message-bubble.received .message-time {
  justify-content: flex-start;
}
</style>