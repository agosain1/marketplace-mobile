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

          <!-- Search Box -->
          <div class="q-mb-lg">
            <q-input
              v-model="searchQuery"
              placeholder="Search listings..."
              outlined
              clearable
              @keyup.enter="searchListings"
              class="q-mb-sm"
            >
              <template v-slot:append>
                <q-btn
                  flat
                  dense
                  round
                  icon="search"
                  @click="searchListings"
                  :loading="searchLoading"
                />
              </template>
            </q-input>
            <q-btn
              v-if="isSearching"
              flat
              label="Show All Listings"
              @click="clearSearch"
              color="grey-6"
              size="sm"
            />
          </div>
          <div class="row">
            <div
              v-for="(listing, index) in response"
              :key="index"
              class="col-xs-12 col-sm-6 col-md-4 col-lg-3"
            >
              <div class="q-pa-sm">
                <q-card class="full-height cursor-pointer" @click="goToListing(listing.listing.id)">
            <q-card-section>
              <div v-if="listing.listing.images && listing.listing.images.length > 0" class="q-mb-md" style="height: 150px;">
                <!-- Image Carousel -->
                <q-carousel
                  v-if="listing.listing.images.length > 1"
                  v-model="imageSlides[index]"
                  swipeable
                  animated
                  arrows
                  navigation
                  height="150px"
                  @click.stop
                >
                  <q-carousel-slide
                    v-for="(image, imgIndex) in listing.listing.images"
                    :key="imgIndex"
                    :name="imgIndex"
                    class="column no-wrap flex-center"
                  >
                    <q-img
                      :src="image"
                      :alt="`${listing.listing.title} - Image ${imgIndex + 1}`"
                      fit="cover"
                      style="height: 150px; width: 100%;"
                      class="rounded-borders"
                    />
                  </q-carousel-slide>
                </q-carousel>

                <!-- Single Image -->
                <q-img
                  v-else
                  :src="listing.listing.images[0]"
                  :alt="listing.listing.title"
                  fit="cover"
                  style="height: 150px; width: 100%;"
                  class="rounded-borders"
                />
              </div>
              <div class="text-h6">{{ listing.listing.title }}</div>
              <div class="text-subtitle2">{{ "$" + listing.listing.price + " " + listing.listing.currency
                }}</div>
              <div class="text-subtitle2">{{ listing.listing.location }}</div>
              <div v-if="listing.dist_away" class="text-subtitle2">{{ listing.dist_away + " miles away"}}</div>

            </q-card-section>
            <q-card-actions align="right">
              <q-btn
                v-if="isLoggedIn && listing.seller.email !== currentUserEmail"
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
import { api } from 'src/boot/axios'
import { useAuthStore } from 'stores/authStore.js'
import MessageSellerDialog from 'src/components/MessageSellerDialog.vue'


export default {
  name: "IndexPage",
  components: {
    MessageSellerDialog
  },
  data() {
    return {
      leftDrawerOpen: false,
      response: [],
      imageSlides: {}, // Track current slide for each listing's carousel
      unreadCount: 0,
      currentUserEmail: null,
      showMessageDialog: false,
      selectedSeller: {},
      selectedListing: {},
      searchQuery: '',
      searchLoading: false,
      isSearching: false,
    }
  },
  computed: {
    isLoggedIn() {
      const authStore = useAuthStore()
      return authStore.isLoggedIn
    }
  },
  watch: {
    // Watch for auth changes and reload listings with proper user_id
    isLoggedIn(newValue, oldValue) {
      // Only reload if auth state actually changed
      if (newValue !== oldValue) {
        this.getCurrentUser().then(() => {
          this.getListings()
          this.getUnreadCount()
        })
      }
    }
  },
  methods: {
    async getListings() {
      try {
        const authStore = useAuthStore()
        const res = await api.get(`listings`, {
          params: {
            user_id: authStore.user ? authStore.user.id : null,
            lat: 37, // TEMP PLACEHOLDERS
            lon: -121,
            dist: 100
          }
        })
        console.log("API response:", res.data) // Debug log

        // Ensure listings is always an array
        this.response = Array.isArray(res.data) ? res.data : []

        // Initialize image slides for each listing
        const slides = {}
        this.response.forEach((listing, index) => {
          slides[index] = 0 // Start at first image
        })
        this.imageSlides = slides
      } catch (e) {
        console.error("Error fetching listings:", e)
        this.response = [] // Fallback to empty array on error
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
        const res = await api.get(`messages/unread-count`)
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
        name: `${listing.seller.fname} ${listing.seller.lname}`,
        email: listing.seller.email
      }
      this.selectedListing = {
        title: listing.listing.title,
        price: listing.listing.price,
        currency: listing.listing.currency
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
        const authStore = useAuthStore()
        this.currentUserEmail = authStore.user?.email || null
      } catch (e) {
        console.error("Error getting current user:", e)
        this.currentUserEmail = null
      }
    },

    async searchListings() {
      if (!this.searchQuery.trim()) {
        return
      }

      this.searchLoading = true
      this.isSearching = true

      try {
        const authStore = useAuthStore()
        const res = await api.get(`listings/search`, {
          params: {
            q: this.searchQuery.trim(),
            user_id: authStore.user ? authStore.user.id : null
          }
        })

        // Ensure listings is always an array
        this.response = Array.isArray(res.data) ? res.data : []

        // Initialize image slides for search results
        const slides = {}
        this.response.forEach((listing, index) => {
          slides[index] = 0 // Start at first image
        })
        this.imageSlides = slides

      } catch (e) {
        console.error("Error searching listings:", e)
        this.response = []
      } finally {
        this.searchLoading = false
      }
    },

    async clearSearch() {
      this.searchQuery = ''
      this.isSearching = false
      await this.getListings() // Load all listings again
    }
  },
  async mounted() {
    // Wait a bit for auth store to be populated from validateToken
    setTimeout(async () => {
      await this.getCurrentUser()    // get current user info first
      this.getListings()             // then fetch filtered listings
      this.getUnreadCount()          // fetch unread count on mount
    }, 100) // Small delay to ensure auth store is populated

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
