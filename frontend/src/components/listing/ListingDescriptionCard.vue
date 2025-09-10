<template>
  <q-card v-if="listing && seller" class="card">
    <q-card-section class="card-section">
      <div>
        <h4 class="q-my-none">{{ listing.title }}</h4>
        <h6 class="q-my-none">{{ '$' + listing.price }}</h6>
        <p class="q-ma-none">
          {{ listing.description }}
        </p>
      </div>

      <div class="description-tags">
        <q-chip
          dense
          :clickable="false"
          v-for="condition in [listing.condition]"
          :key="condition"
          class="q-mx-none"
          outline
        >
          Condition: {{ condition }}
        </q-chip>
        <q-chip
          dense
          :clickable="false"
          v-for="category in [listing.category]"
          :key="category"
          class="q-mx-none"
          outline
        >
          {{ category }}
        </q-chip>
      </div>

      <div>
        Listed by
        <router-link :to="'/users/' + seller.id">
          {{ seller.fname + ' ' + seller.lname }}
        </router-link>
      </div>
    </q-card-section>
    <q-card-section class="q-pt-none card-section">
      <h5 class="q-my-none">Location</h5>
      <listing-map
        :latitude="listing.latitude ? Number(listing.latitude) : undefined"
        :longitude="listing.longitude ? Number(listing.longitude) : undefined"
      />
    </q-card-section>
    <q-card-section class="q-pt-none footer">
      <div v-if="listing.created_at">
        Posted: {{ listing.created_at?.toDateString() }}
        <span v-if="listing.updated_at"> | Updated: {{ listing.updated_at?.toDateString() }}</span>
      </div>
      <div>
        <q-icon name="visibility" class="" /><span style="margin-left: 0.25rem">
          {{ listing.views ?? 0 }}
        </span>
      </div>
    </q-card-section>
  </q-card>
  <q-skeleton v-else type="rect" class="col-grow" />
</template>

<script setup lang="ts">
import { QSkeleton, QChip, QIcon } from 'quasar';
import { RouterLink } from 'vue-router';
import ListingMap from './ListingMap.vue';
import type { _TODO_LISTING_MODEL, _TODO_USER_MODEL } from 'src/types';

const { listing } = defineProps<{
  listing: _TODO_LISTING_MODEL | undefined;
  seller: _TODO_USER_MODEL | undefined;
}>();
</script>

<style scoped lang="scss">
.card {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}
.views-section {
  margin-top: auto;
}
.card-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.description-tags {
  display: flex;
  gap: 0.5rem;
}
.footer {
  margin-top: auto;
  gap: 0.5rem;
  color: $footer;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
