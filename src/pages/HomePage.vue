<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" @click="leftDrawerOpen = !leftDrawerOpen" class="relative-position">
          <div
            v-if="unreadCount > 0 && isLoggedIn"
            class="absolute"
            style="top: 6px; left: 2px; width: 8px; height: 8px; background-color: red; border-radius: 50%;"
          ></div>
        </q-btn>
        <q-toolbar-title style="cursor: pointer" @click="goHome">Unimarket</q-toolbar-title>
        <q-btn v-if="!isLoggedIn" flat @click="goToLogin"> Login </q-btn>
        <template v-else>
          <q-btn flat dense round @click="goToMessages" class="relative-position">
            <q-icon name="message" />
            <div
              v-if="unreadCount > 0"
              class="absolute"
              style="top: 6px; left: 2px; width: 8px; height: 8px; background-color: red; border-radius: 50%;"
            ></div>
          </q-btn>
          <q-btn flat dense round icon="account_circle" @click="goToAccount" />
        </template>
        <q-btn flat dense round icon="add" @click="goToAddListing" />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" side="left" bordered>
      <q-list>
        <q-item clickable v-ripple @click="goHome">
          <q-item-section>Home</q-item-section>
        </q-item>
        <q-item clickable v-ripple @click="goToMyListings">
          <q-item-section>My Listings</q-item-section>
        </q-item>
        <q-item v-if="isLoggedIn" clickable v-ripple @click="goToMessages" class="relative-position">
          <q-item-section>Messages</q-item-section>
          <div
            v-if="unreadCount > 0"
            class="absolute"
            style="top: 12px; left: 8px; width: 8px; height: 8px; background-color: red; border-radius: 50%;"
          ></div>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <q-page>
        <div class="q-pa-lg">
          <h4>Current Listings</h4>
          <div class="row">
            <div
              v-for="(listing, index) in listings"
              :key="index"
              class="col-xs-12 col-sm-6 col-md-4 col-lg-3"
            >
              <div class="q-pa-sm">
                <q-card class="full-height cursor-pointer" @click="goToListing(listing.id)">
            <q-card-section>
              <div v-if="listing.images && listing.images.length > 0" class="q-mb-md" style="height: 150px;">
                <!-- Image Carousel -->
                <q-carousel
                  v-if="listing.images.length > 1"
                  v-model="imageSlides[index]"
                  swipeable
                  animated
                  arrows
                  navigation
                  height="150px"
                  @click.stop
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
                      style="height: 150px; width: 100%;"
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
                  style="height: 150px; width: 100%;"
                  class="rounded-borders"
                />
              </div>
              <div class="text-h6">{{ listing.title }}</div>
              <div class="text-subtitle2">{{ "$" + listing.price + " " + listing.currency }}</div>
              <div class="text-subtitle2">{{ listing.location }}</div>

            </q-card-section>
            <q-card-actions align="right">
              <q-btn
                v-if="isLoggedIn && listing.seller_email !== currentUserEmail"
                flat
                color="primary"
                icon="message"
                label="Message Seller"
                @click.stop="messageSeller(listing)"
              />
            </q-card-actions>
                </q-card>
              </div>
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
import axios from "axios"
import { API_URL } from '../../constants.js'
import { formatDate } from '../utils/dateUtils.js'
import MessageSellerDialog from 'src/components/MessageSellerDialog.vue'


export default {
  name: "IndexPage",
  components: {
    MessageSellerDialog
  },
  data() {
    return {
      leftDrawerOpen: false,
      listings: [],
      imageSlides: {}, // Track current slide for each listing's carousel
      unreadCount: 0,
      currentUserEmail: null,
      showMessageDialog: false,
      selectedSeller: {},
      selectedListing: {},
    }
  },
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('auth_token')
    }
  },
  methods: {
    async getListings() {
      try {
        const res = await axios.get(`${API_URL}listings`)
        console.log("API response:", res.data) // Debug log

        // Ensure listings is always an array
        let allListings = Array.isArray(res.data) ? res.data : []

        // Filter out current user's listings if logged in
        if (this.isLoggedIn && this.currentUserEmail) {
          this.listings = allListings.filter(listing => listing.seller_email !== this.currentUserEmail)
        } else {
          this.listings = allListings
        }

        // Initialize image slides for each listing
        const slides = {}
        this.listings.forEach((listing, index) => {
          slides[index] = 0 // Start at first image
        })
        this.imageSlides = slides
      } catch (e) {
        console.error("Error fetching listings:", e)
        this.listings = [] // Fallback to empty array on error
      }
    },
    goToAddListing() {
      if (this.isLoggedIn) {
        this.$router.push("/add")
      } else {
        this.$router.push("/login")
      }
    },
    goToLogin() {
      this.$router.push('/login')
    },
    goToAccount() {
      this.$router.push('/account')
    },
    goHome() {
      this.$router.push('/')
    },
    goToMyListings() {
      this.$router.push('/my-listings')
    },
    goToMessages() {
      this.$router.push('/messages')
    },
    async getUnreadCount() {
      if (!this.isLoggedIn) {
        this.unreadCount = 0
        return
      }

      try {
        const token = localStorage.getItem('auth_token')
        const res = await axios.get(`${API_URL}messages/unread-count`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        this.unreadCount = res.data.unread_count || 0
      } catch (e) {
        console.error("Error fetching unread count:", e)
        this.unreadCount = 0
      }
    },
    goToListing(listingId) {
      this.$router.push(`/listing/${listingId}`)
    },
    messageSeller(listing) {
      // Set up dialog data and show it
      this.selectedSeller = {
        name: listing.seller_name,
        email: listing.seller_email
      }
      this.selectedListing = {
        title: listing.title,
        price: listing.price,
        currency: listing.currency
      }
      this.showMessageDialog = true
    },
    onMessageSent() {
      // Handle successful message sent
      // Could refresh unread count or show additional feedback
      this.getUnreadCount()
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
    formatDate
  },
  async mounted() {
    await this.getCurrentUser()    // get current user info first
    this.getListings()             // then fetch filtered listings
    this.getUnreadCount()          // fetch unread count on mount

    // Listen for message updates from other pages
    this.handleStorageChange = (e) => {
      if (e.key === 'messages_updated') {
        this.getUnreadCount()
      }
    }
    window.addEventListener('storage', this.handleStorageChange)

    // Optional: Poll every 10 seconds to always show current listings and unread count
    this.polling = setInterval(() => {
      this.getListings()
      this.getUnreadCount()
    }, 10000) // 10000 = 10s
  },
  beforeUnmount() {
    clearInterval(this.polling)
    window.removeEventListener('storage', this.handleStorageChange)
  }
}
</script>
