<template>
  <q-page class="col q-gutter-xl q-pb-xl">
    <div class="row q-gutter-xl">
      <market-filters />
      <market-listings :listings="listings" />
    </div>
    <q-pagination
      v-if="page > 1"
      v-model="page"
      :max="maxPage"
      :boundary-numbers="true"
      :max-pages="5"
      class="flex flex-center"
      direction-links
    />
  </q-page>
</template>

<script setup lang="ts">
import MarketFilters from 'src/components/market/MarketFilters.vue';
import MarketListings from 'src/components/market/MarketListings.vue';
import { ref, onMounted } from 'vue';
import { MOCK_API_CALL_GET_LISTINGS } from 'src/mock/listings';
import type { _TODO_LISTING_MODEL } from 'src/types';

const listings = ref<_TODO_LISTING_MODEL[] | undefined>(undefined);

onMounted(async () => {
  // Simulate fetching data from an API
  listings.value = await MOCK_API_CALL_GET_LISTINGS();
});

const page = ref(1);
const maxPage = 1;
</script>

<style scoped lang="scss"></style>
