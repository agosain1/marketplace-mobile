<template>
  <q-carousel
    v-if="listing && listing.images"
    v-model="carouselIndex"
    :swipeable="listing.images.length > 1"
    :arrows="listing.images.length > 1"
    :navigation="listing.images.length > 1"
    width="100%"
    height="100%"
  >
    <q-carousel-slide v-for="(image, i) in listing.images" :key="i" :name="i" class="q-pa-none">
      <q-img
        :src="image"
        :alt="`${listing.title} - Image ${i + 1}`"
        :fit="fit"
        class="rounded-borders"
        width="100%"
        height="100%"
      />
    </q-carousel-slide>
  </q-carousel>
  <q-skeleton v-else class="rounded-borders" />
</template>

<script setup lang="ts">
import { QCarousel, QCarouselSlide, QSkeleton } from 'quasar';
import type { _TODO_LISTING_MODEL } from 'src/types';
import { ref } from 'vue';

const { listing, fit = 'cover' } = defineProps<{
  listing: _TODO_LISTING_MODEL | undefined;
  fit?: 'cover' | 'contain';
}>();

const carouselIndex = ref(0);
</script>
