<template>
  <q-chip dense size="sm" icon="location_on" class="q-ma-none">
    {{ location }}
  </q-chip>
</template>

<script setup lang="ts">
import { QChip } from 'quasar';
const { location = 'Location' } = defineProps<{
  location: string | null;
}>();
</script>

<style scoped lang="scss"></style>
