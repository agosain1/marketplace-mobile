<template>
  <q-card :key="listing.id" class="listing-card">
    <q-card-section class="q-pb-none">
      <q-responsive :ratio="1 / 1">
        <!-- make it a surface, perahps card surrounding -->
        <listing-images :listing="listing" />
      </q-responsive>
    </q-card-section>

    <q-card-section class="q-pt-sm q-pb-none row">
      <div class="col">
        <router-link :to="listingLink" class="text-caption text-black">
          {{ listing.title }}
        </router-link>

        <location-label :location="listing.location" />
      </div>
      <div class="text-h6">{{ '$' + listing.price }}</div>
    </q-card-section>

    <q-card-actions>
      <q-btn :to="listingLink" label="View listing" unelevated class="full-width" />
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import LocationLabel from '../LocationChip.vue';
import ListingImages from '../ListingImages.vue';
import type { _TODO_LISTING_MODEL } from 'src/types';
import { RouterLink } from 'vue-router';

const { listing } = defineProps<{
  listing: _TODO_LISTING_MODEL;
}>();

const listingLink = `/listing/${listing?.id}`;
</script>

<style scoped lang="scss">
.listing-card {
  background-color: $secondary;
}
</style>
