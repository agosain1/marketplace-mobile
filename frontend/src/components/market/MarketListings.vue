<template>
  <div class="col">
    <h3 class="q-mt-none q-mb-md">Current Listings</h3>
    <q-input v-model="search" label="Search listings" type="search" rounded class="q-mb-md">
      <template v-slot:append>
        <q-icon v-if="search === ''" name="search" />
        <q-icon v-else name="clear" class="cursor-pointer" @click="search = ''" />
      </template>
    </q-input>

    <div v-if="listings === undefined" class="row q-col-gutter-md q-row-gutter-md">
      <div v-for="n in 12" :key="'skeleton-listing-' + n" class="col-xs-12 col-sm-6 col-lg-4">
        <q-skeleton
          type="rect"
          :key="'skeleton-listing-' + n"
          class="col-sm-6 col-lg-4"
          height="342px"
          animation="blink"
        />
      </div>
    </div>
    <div v-else-if="listings.length > 0" class="row q-col-gutter-md q-row-gutter-md">
      <div
        v-for="(listing, index) in listings"
        :key="'listing-' + index"
        class="col-xs-12 col-sm-6 col-lg-4"
      >
        <listing-card :listing="listing" />
      </div>
    </div>
    <div v-else>
      <footer>No listings found. Please try again.</footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { QSkeleton } from 'quasar';
import ListingCard from 'src/components/market/ListingCard.vue';
import type { _TODO_LISTING_MODEL } from 'src/types';

const { listings } = defineProps<{
  listings: _TODO_LISTING_MODEL[] | undefined;
}>();

const search = defineModel<string>('search');
</script>
