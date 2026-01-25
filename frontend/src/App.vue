<script setup>
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useAuth } from './composables/useAuth'

const { fetchMe, startTokenValidation } = useAuth()

onMounted(async () => {
  // Fetch user data from HTTP-only cookie on app startup
  await fetchMe()

  // Start periodic token validation
  startTokenValidation()
})
</script>

<template>
  <RouterView />
</template>
