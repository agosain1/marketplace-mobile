<script setup>
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useAuth } from './composables/useAuth'

const { validateToken, startTokenValidation } = useAuth()

onMounted(async () => {
  // Try to validate token from HTTP-only cookie on app startup
  await validateToken()
  
  // Start periodic token validation
  startTokenValidation()
})
</script>

<template>
  <RouterView />
</template>
