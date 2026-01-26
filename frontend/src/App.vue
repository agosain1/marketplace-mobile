<script setup>
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useAuth } from './composables/useAuth'

const { startTokenValidation } = useAuth()

onMounted(() => {
  // Don't call fetchMe here - the router guard handles it
  // Just start periodic token validation
  startTokenValidation()
})
</script>

<template>
  <RouterView />
</template>
