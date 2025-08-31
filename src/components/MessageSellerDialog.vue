<template>
  <q-dialog v-model="showDialog" persistent>
    <q-card style="min-width: 350px; max-width: 500px;">
      <q-card-section>
        <div class="text-h6">Message Seller</div>
      </q-card-section>

      <q-card-section>
        <div class="q-mb-md">
          <div class="text-subtitle2 text-weight-medium">To: {{ seller.name || seller.email }}</div>
          <div class="text-caption text-grey-6">{{ seller.email }}</div>
        </div>
        
        <div class="q-mb-md">
          <div class="text-subtitle2 text-weight-medium">About: {{ listing.title }}</div>
          <div class="text-caption text-grey-6">${{ listing.price }} {{ listing.currency }}</div>
        </div>

        <q-input
          v-model="messageContent"
          type="textarea"
          label="Your message"
          outlined
          autogrow
          rows="4"
          :placeholder="messagePlaceholder"
          class="q-mt-md"
        />
      </q-card-section>

      <q-card-actions align="right" class="text-primary">
        <q-btn flat label="Cancel" @click="closeDialog" />
        <q-btn
          flat
          label="Send Message"
          @click="sendMessage"
          :loading="sending"
          :disable="!messageContent.trim()"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { api } from 'src/boot/axios'
import { useQuasar } from 'quasar'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  seller: {
    type: Object,
    required: true,
    default: () => ({})
  },
  listing: {
    type: Object,
    required: true,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'message-sent'])

const $q = useQuasar()

// Reactive data
const showDialog = ref(false)
const messageContent = ref('')
const sending = ref(false)

// Computed
const messagePlaceholder = computed(() => {
  return `Hi! I'm interested in your "${props.listing.title}" listing. Is it still available?`
})

// Watch for prop changes
watch(() => props.modelValue, (newVal) => {
  showDialog.value = newVal
  if (newVal) {
    // Pre-fill with a friendly message
    messageContent.value = messagePlaceholder.value
  } else {
    // Clear message when dialog closes
    messageContent.value = ''
  }
})

watch(showDialog, (newVal) => {
  emit('update:modelValue', newVal)
})

// Methods
const closeDialog = () => {
  showDialog.value = false
  messageContent.value = ''
}

const sendMessage = async () => {
  if (!messageContent.value.trim() || sending.value) return

  sending.value = true

  try {
    const token = localStorage.getItem('auth_token')
    if (!token) {
      $q.notify({
        color: 'negative',
        message: 'Please log in to send messages'
      })
      return
    }

    await api.post('/messages/send', {
      receiver_email: props.seller.email,
      content: messageContent.value.trim()
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    $q.notify({
      color: 'positive',
      message: 'Message sent successfully!',
      position: 'top'
    })

    emit('message-sent')
    closeDialog()

  } catch (error) {
    console.error('Error sending message:', error)
    $q.notify({
      color: 'negative',
      message: 'Failed to send message. Please try again.',
      position: 'top'
    })
  } finally {
    sending.value = false
  }
}
</script>

<style scoped>
/* Add any custom styling here if needed */
</style>