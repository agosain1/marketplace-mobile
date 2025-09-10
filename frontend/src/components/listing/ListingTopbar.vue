<template>
  <div class="row justify-between items-center topbar">
    <listing-breadcrumbs :listing="listing" />
    <q-btn-group flat>
      <q-btn icon="share" round />
      <q-btn icon="bookmark" round />
    </q-btn-group>
  </div>
</template>

<script setup lang="ts">
import { QBtnGroup, QBtn } from 'quasar';
import ListingBreadcrumbs from 'src/components/listing/ListingBreadcrumbs.vue';
import type { _TODO_LISTING_MODEL } from 'src/types';

const { listing } = defineProps<{
  listing: _TODO_LISTING_MODEL | undefined;
}>();
</script>

<style scoped lang="scss">
.topbar {
  height: 25px;
}
</style>
