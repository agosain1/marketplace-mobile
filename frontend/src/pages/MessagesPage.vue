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
                    {{ (conversation.other_user_name || conversation.other_user_email).charAt(0).toUpperCase() }}
                  </q-avatar>
                </q-item-section>

                <q-item-section>
                  <q-item-label class="text-weight-medium">
                    {{ conversation.other_user_name || conversation.other_user_email }}
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
                  {{ (selectedConversationName || selectedConversation).charAt(0).toUpperCase() }}
                  <q-badge v-if="isOtherUserOnline" color="green" floating rounded />
                </q-avatar>
                <q-toolbar-title class="q-ml-sm">
                  {{ selectedConversationName || selectedConversation }}
                  <div v-if="isOtherUserOnline" class="text-caption text-grey-7">online</div>
                </q-toolbar-title>
                <q-chip
                  :color="isConnected ? 'green' : 'orange'"
                  text-color="white"
                  size="sm"
                  :icon="isConnected ? 'wifi' : 'wifi_off'"
                >
                  {{ isConnected ? 'Live' : 'Offline' }}
                </q-chip>
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

                  <!-- Typing Indicator -->
                  <div v-if="isOtherUserTyping" class="typing-indicator q-pa-sm">
                    <q-spinner-dots color="primary" size="20px" />
                    <span class="q-ml-sm text-caption text-grey-7">typing...</span>
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
                  @input="onTyping"
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
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'stores/authStore.js'
import { useMessagesStore } from 'stores/messagesStore.js'
import { storeToRefs } from 'pinia'

const router = useRouter()
const authStore = useAuthStore()
const messagesStore = useMessagesStore()

// Get reactive state from messages store
const {
  conversations,
  currentMessages,
  selectedConversation,
  selectedConversationName,
  selectedConversationId,
  isConnected,
  typingUsers,
  onlineUsers
} = storeToRefs(messagesStore)

// Local component state
const newMessage = ref('')
const sendingMessage = ref(false)
const showNewMessageDialog = ref(false)
const newMessageEmail = ref('')
const newMessageContent = ref('')
const messagesScrollArea = ref(null)
const typingTimeout = ref(null)

// Computed properties
const currentUserId = computed(() => authStore.user?.id)

const isOtherUserTyping = computed(() => {
  return selectedConversationId.value && typingUsers.value[selectedConversationId.value]
})

const isOtherUserOnline = computed(() => {
  return selectedConversationId.value && onlineUsers.value.has(selectedConversationId.value)
}) // could remove if not necessary (typing doesnt work)

const goHome = () => {
  router.push('/')
}

const refreshMessages = async () => {
  await messagesStore.loadConversations()
  if (selectedConversation.value) {
    await messagesStore.loadConversation(selectedConversation.value)
  }
}

const selectConversation = async (email) => {
  await messagesStore.selectConversation(email)

  // Scroll to bottom after loading
  await nextTick()
  scrollToBottom()
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || !selectedConversation.value || sendingMessage.value) return

  sendingMessage.value = true

  try {
    // Use WebSocket by default, falls back to REST if disconnected
    const success = await messagesStore.sendMessage(selectedConversation.value, newMessage.value.trim())

    if (success) {
      newMessage.value = ''

      // Stop typing indicator
      if (selectedConversationId.value) {
        messagesStore.stopTyping(selectedConversationId.value)
      }

      // Scroll to bottom
      await nextTick()
      scrollToBottom()
    }
  } catch (error) {
    console.error('Error sending message:', error)
  } finally {
    sendingMessage.value = false
  }
}

const sendNewMessage = async () => {
  if (!newMessageEmail.value.trim() || !newMessageContent.value.trim() || sendingMessage.value) return

  sendingMessage.value = true

  try {
    // Use WebSocket by default, falls back to REST if disconnected
    const success = await messagesStore.sendMessage(newMessageEmail.value.trim(), newMessageContent.value.trim())

    if (success) {
      const recipientEmail = newMessageEmail.value.trim()

      showNewMessageDialog.value = false
      newMessageEmail.value = ''
      newMessageContent.value = ''

      // Select the new conversation
      await messagesStore.selectConversation(recipientEmail)

      // Scroll to bottom
      await nextTick()
      scrollToBottom()
    }
  } catch (error) {
    console.error('Error sending new message:', error)
  } finally {
    sendingMessage.value = false
  }
}

const onTyping = () => {
  if (!selectedConversationId.value) return

  // Send typing start
  messagesStore.startTyping(selectedConversationId.value)

  // Clear previous timeout
  if (typingTimeout.value) {
    clearTimeout(typingTimeout.value)
  }

  // Auto-stop typing after 1 second of inactivity
  typingTimeout.value = setTimeout(() => {
    messagesStore.stopTyping(selectedConversationId.value)
  }, 1000)
}

const scrollToBottom = () => {
  if (messagesScrollArea.value) {
    messagesScrollArea.value.setScrollPercentage('vertical', 1)
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

// Watch for new messages to auto-scroll
watch(currentMessages, async () => {
  await nextTick()
  scrollToBottom()
}, { deep: true })

// Load data on mount
onMounted(async () => {
  // Get current user ID from auth store
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }

  // Load conversations from store
  await messagesStore.loadConversations()

  // Check if we should start a new conversation from query params
  const route = router.currentRoute.value
  if (route.query.start_conversation) {
    const sellerEmail = route.query.start_conversation

    // Open the new message dialog with pre-filled seller email
    newMessageEmail.value = sellerEmail
    showNewMessageDialog.value = true

    // Clear the query params to avoid re-opening on refresh
    router.replace({ path: '/messages' })
  }
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
