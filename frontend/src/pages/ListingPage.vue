<template>
  <q-page class="col q-gutter-xl q-py-xl">
    <listing-topbar :listing="listing" />
    <q-separator color="primary" class="q-mt-md" />
    <div class="row top-container">
      <!-- eventually change so that controls are outside image and clearly visible -->
      <listing-images class="rounded-borders images col-grow" :listing="listing" fit="contain" />
      <listing-description-card class="" :listing="listing" :seller="seller" />
    </div>
    <div>reviews / comments / anything else</div>
    <div>explore other options</div>
  </q-page>
</template>

<script setup lang="ts">
import { QSeparator } from 'quasar';
import ListingDescriptionCard from 'src/components/listing/ListingDescriptionCard.vue';
import ListingTopbar from 'src/components/listing/ListingTopbar.vue';
import ListingImages from 'src/components/ListingImages.vue';
import { MOCK_API_CALL_GET_LISTING } from 'src/mock/listing';
import type { _TODO_LISTING_MODEL, _TODO_USER_MODEL } from 'src/types';
import { ref, onMounted } from 'vue';

const listing = ref<_TODO_LISTING_MODEL>();
const seller = ref<_TODO_USER_MODEL>();

onMounted(async () => {
  // Simulate fetching data from an API
  const data = await MOCK_API_CALL_GET_LISTING();
  listing.value = data.listing;
  seller.value = data.seller;
});
</script>

<style scoped lang="scss">
.images {
  background-color: $primary;
  aspect-ratio: 1/1;

  width: 100%;

  /* laptop size and up */
  @media (min-width: 1024px) {
    max-width: 40%;
  }
}

.top-container {
  display: flex;
  gap: 48px;
  flex-wrap: nowrap;
}
</style>
