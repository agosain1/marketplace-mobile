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
          <q-card class="q-mb-lg">
            <!-- Images Section -->
            <div v-if="listing.images && listing.images.length > 0" class="q-mb-md">
              <!-- Image Carousel for multiple images -->
              <q-carousel
                v-if="listing.images.length > 1"
                v-model="currentSlide"
                swipeable
                animated
                arrows
                navigation
                height="300px"
                class="bg-grey-1 shadow-2 rounded-borders"
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
                    fit="cover"
                    style="height: 300px; width: 100%;"
                    class="rounded-borders"
                  />
                </q-carousel-slide>
              </q-carousel>

              <!-- Single Image -->
              <q-img
                v-else
                :src="listing.images[0]"
                :alt="listing.title"
                fit="cover"
                style="height: 300px; width: 100%;"
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

            <!-- Title and Price -->
            <q-card-section>
              <div class="text-h4 q-mb-sm">{{ listing.title }}</div>
              <div class="text-h5 text-green-7 q-mb-md">${{ listing.price }} {{ listing.currency }}</div>
            </q-card-section>

            <!-- Details -->
            <q-card-section>
              <q-list dense>
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="description" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Description</q-item-label>
                    <q-item-label caption class="text-wrap">{{ listing.description }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="category" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Category</q-item-label>
                    <q-item-label caption>{{ listing.category }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="place" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Location</q-item-label>
                    <q-item-label caption>{{ listing.location }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="star" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Condition</q-item-label>
                    <q-item-label caption>{{ listing.condition }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="info" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Status</q-item-label>
                    <q-item-label caption>{{ listing.status }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="visibility" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Views</q-item-label>
                    <q-item-label caption>{{ listing.views }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="person" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Seller</q-item-label>
                    <q-item-label caption>{{ listing.seller_name || 'Unknown' }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="schedule" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Created</q-item-label>
                    <q-item-label caption>{{ formatDate(listing.created_at) }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="update" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Last Updated</q-item-label>
                    <q-item-label caption>{{ formatDate(listing.updated_at) }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>

            <!-- Actions -->
            <q-card-actions align="right">
              <q-btn
                v-if="isLoggedIn && listing.seller_email !== currentUserEmail"
                color="primary"
                icon="message"
                label="Message Seller"
                @click="messageSeller"
                class="q-ma-sm"
              />
            </q-card-actions>
          </q-card>
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
import axios from "axios"
import { API_URL } from '../../constants.js'
import { formatDate } from '../utils/dateUtils.js'
import MessageSellerDialog from 'src/components/MessageSellerDialog.vue'

export default {
  name: "ListingDetail",
  components: {
    MessageSellerDialog
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
      return !!localStorage.getItem('auth_token')
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

        const res = await axios.get(`${API_URL}listings/${this.listingId}`)
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
        const token = localStorage.getItem('auth_token')
        const payload = JSON.parse(atob(token.split('.')[1]))
        this.currentUserEmail = payload.email
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
