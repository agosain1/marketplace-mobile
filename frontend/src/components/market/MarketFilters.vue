<template>
  <q-card class="sticky-fit col-12 col-md-3">
    <q-card-section class="q-pa-md col">
      TODO: Filter
      <q-separator spaced />
      TODO: FILTER
      <q-separator spaced />
      TODO: FILTER
      <q-separator spaced />
      TODO: FILTER
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { QCard, QCardSection, QSeparator } from 'quasar';
</script>

<style scoped lang="scss">
.sticky-fit {
  align-self: flex-start;
  position: static;
  //   width: fit-content;

  @media (min-width: 1024px) {
    position: sticky;
    z-index: 10;
    top: 100px;
  }
}
</style>
