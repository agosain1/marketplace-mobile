<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="arrow_back" @click="goBack" />
        <q-toolbar-title>{{ listing?.title || 'Loading...' }}</q-toolbar-title>
        <q-btn v-if="!isLoggedIn" flat @click="goToLogin"> Login </q-btn>
        <q-btn v-else flat dense round icon="account_circle" @click="goToAccount" />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page>
        <div v-if="loading" class="flex flex-center q-mt-xl">
          <q-spinner-dots size="50px" color="primary" />
          <p class="q-ml-md">Loading listing...</p>
        </div>

        <div v-else-if="error" class="flex flex-center q-mt-xl">
          <q-card style="max-width: 400px;">
            <q-card-section class="text-center">
              <q-icon name="error" size="64px" color="negative" class="q-mb-md" />
              <h5 class="q-mt-none q-mb-sm">Error Loading Listing</h5>
              <p class="text-grey-7 q-mb-lg">{{ error }}</p>
              <q-btn label="Go Back" color="primary" @click="goBack" />
            </q-card-section>
          </q-card>
        </div>

        <div v-else-if="listing" class="q-pa-lg">
          <div class="row q-col-gutter-lg">
            <!-- Left side - Images -->
            <div class="col-xs-12 col-sm-8 col-md-8 col-lg-8">
              <q-card class="full-height">
                <!-- Images Section -->
                <div v-if="listing.images && listing.images.length > 0" class="full-height">
                  <!-- Image Carousel for multiple images -->
                  <q-carousel
                    v-if="listing.images.length > 1"
                    v-model="currentSlide"
                    :swipeable="$q.screen.xs"
                    animated
                    arrows
                    navigation
                    height="600px"
                    class="bg-grey-1 shadow-2 rounded-borders carousel-with-arrows full-height"
                  >
                    <q-carousel-slide
                      v-for="(image, imgIndex) in listing.images"
                      :key="imgIndex"
                      :name="imgIndex"
                      class="column no-wrap flex-center"
                    >
                      <q-img
                        :src="image"
                        :alt="`${listing.title} - Image ${imgIndex + 1}`"
                        fit="contain"
                        style="max-height: 600px; width: 100%;"
                        class="rounded-borders"
                      />
                    </q-carousel-slide>
                  </q-carousel>

                  <!-- Single Image -->
                  <q-img
                    v-else
                    :src="listing.images[0]"
                    :alt="listing.title"
                    fit="contain"
                    style="height: 600px; width: 100%;"
                    class="rounded-borders"
                  />

                  <!-- Image Counter -->
                  <div v-if="listing.images.length > 1" class="absolute-top-right q-ma-sm">
                    <q-chip
                      dense
                      color="black"
                      text-color="white"
                      icon="photo"
                      :label="`${currentSlide + 1}/${listing.images.length}`"
                    />
                  </div>
                </div>
              </q-card>
            </div>

            <!-- Right side - All Information -->
            <div class="col-xs-12 col-sm-4 col-md-4 col-lg-4">
              <q-card class="q-mb-lg">
                <!-- Title and Price -->
                <q-card-section>
                  <div class="">
                    <div class="col">
                      <div class="text-h5 q-mb-sm text-blue-7">{{ listing.title }}</div>
                      <div class="text-h6 text-green-7 q-mb-sm">${{ listing.price }} {{ listing.currency }}</div>
                      <div class="text-body1 text-indigo-7 q-mb-xs">Seller: {{ listing.seller_name || 'Unknown' }}</div>
                      <div class="text-body2 text-grey-7 q-mb-xs">Category: {{ listing.category }}</div>
                      <div class="text-body2 text-grey-7 q-mb-sm">Condition: {{ listing.condition }}</div>
                      <div class="text-blue-7 text-h6 q-mb-xs">Description</div>
                      <div class="text-wrap text-black text-body1 q-mb-md">{{ listing.description }}</div>
                    </div>
                    <div class="col-auto">
                      <q-btn
                        v-if="isLoggedIn && listing.seller_email !== currentUserEmail"
                        color="primary"
                        icon="message"
                        label="Message Seller"
                        @click="messageSeller"
                        size="md"
                      />
                    </div>
                  </div>
                </q-card-section>

                <!-- Location Map Section -->
                <q-card-section v-if="listing.latitude && listing.longitude">
                  <h6 class="q-ma-none q-mb-md text-grey-8">Approximate Location: {{ listing.location }}</h6>
                  <ListingLocationMap
                    :latitude="listing.latitude"
                    :longitude="listing.longitude"
                    :location="listing.location"
                    :zoom="11"
                  />
                </q-card-section>

                <!-- Additional Info Section -->
                <q-card-section>
                  <div class="text-body2 text-grey-7 q-mb-xs">Views: {{ listing.views }}</div>
                  <div class="text-body2 text-grey-7 q-mb-xs">Created: {{ formatDate(listing.created_at) }}</div>
                  <div class="text-body2 text-grey-7">Last Updated: {{ formatDate(listing.updated_at) }}</div>
                </q-card-section>

              </q-card>
            </div>
          </div>
        </div>
      </q-page>
    </q-page-container>

    <!-- Message Seller Dialog -->
    <MessageSellerDialog
      v-model="showMessageDialog"
      :seller="selectedSeller"
      :listing="selectedListing"
      @message-sent="onMessageSent"
    />
  </q-layout>
</template>

<script>
import { api } from 'src/boot/axios'
import { useAuthStore } from 'stores/authStore.js'
import { formatDate } from '../utils/dateUtils.js'
import MessageSellerDialog from 'src/components/MessageSellerDialog.vue'
import ListingLocationMap from 'src/components/ListingLocationMap.vue'

export default {
  name: "ListingDetail",
  components: {
    MessageSellerDialog,
    ListingLocationMap
  },
  data() {
    return {
      listing: null,
      loading: true,
      error: null,
      currentSlide: 0,
      currentUserEmail: null,
      showMessageDialog: false,
      selectedSeller: {},
      selectedListing: {},
    }
  },
  computed: {
    isLoggedIn() {
      const authStore = useAuthStore()
      return authStore.isLoggedIn
    },
    listingId() {
      return this.$route.params.id
    }
  },
  methods: {
    async fetchListing() {
      try {
        this.loading = true
        this.error = null

        const res = await api.get(`listings/${this.listingId}`)
        this.listing = res.data
      } catch (e) {
        console.error("Error fetching listing:", e)
        if (e.response?.status === 404) {
          this.error = "Listing not found"
        } else {
          this.error = "Failed to load listing. Please try again."
        }
      } finally {
        this.loading = false
      }
    },
    goBack() {
      this.$router.go(-1)
    },
    goToLogin() {
      this.$router.push('/login')
    },
    goToAccount() {
      this.$router.push('/account')
    },
    messageSeller() {
      if (!this.listing) return

      // Set up dialog data and show it
      this.selectedSeller = {
        name: this.listing.seller_name,
        email: this.listing.seller_email
      }
      this.selectedListing = {
        title: this.listing.title,
        price: this.listing.price,
        currency: this.listing.currency
      }
      this.showMessageDialog = true
    },
    onMessageSent() {
      // Handle successful message sent
      // Could show additional feedback or update UI
    },
    async getCurrentUser() {
      if (!this.isLoggedIn) {
        this.currentUserEmail = null
        return
      }

      try {
        const authStore = useAuthStore()
        this.currentUserEmail = authStore.user?.email || null
      } catch (e) {
        console.error("Error getting current user:", e)
        this.currentUserEmail = null
      }
    },
    formatDate,
  },
  mounted() {
    this.fetchListing()
    this.getCurrentUser()
  },
  watch: {
    '$route.params.id'() {
      if (this.$route.params.id) {
        this.fetchListing()
      }
    }
  }
}
</script>

<style scoped>
/* Enhanced carousel arrows for desktop */
@media (min-width: 576px) {
  .carousel-with-arrows :deep(.q-carousel__arrow) {
    background: rgba(0, 0, 0, 0.7) !important;
    color: white !important;
    border-radius: 50% !important;
    width: 50px !important;
    height: 50px !important;
    font-size: 24px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
  }

  .carousel-with-arrows :deep(.q-carousel__arrow:hover) {
    background: rgba(0, 0, 0, 0.9) !important;
    transform: translateY(-50%) scale(1.1) !important;
  }

  .carousel-with-arrows :deep(.q-carousel__arrow--left) {
    left: 15px !important;
  }

  .carousel-with-arrows :deep(.q-carousel__arrow--right) {
    right: 15px !important;
  }
}
</style>
