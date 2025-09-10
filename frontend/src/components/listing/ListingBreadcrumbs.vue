<template>
  <q-breadcrumbs gutter="lg">
    <q-breadcrumbs-el label="Listings" icon="storefront" :to="{ path: '/' }" class="text-body" />
    <q-breadcrumbs-el
      :label="listing?.title ?? ''"
      :to="'/listing/' + (listing?.id ?? '')"
      icon="sell"
      class="text-body"
    />
    <q-skeleton
      v-if="listing === undefined"
      type="text"
      width="250px"
      height="48px"
      class="q-pa-none q-mx-none"
    />
  </q-breadcrumbs>
</template>

<script setup lang="ts">
import { QBreadcrumbs, QBreadcrumbsEl, QSkeleton } from 'quasar';
import type { _TODO_LISTING_MODEL } from 'src/types';

const { listing } = defineProps<{
  listing: _TODO_LISTING_MODEL;
}>();
</script>
