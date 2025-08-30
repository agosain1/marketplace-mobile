<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" @click="leftDrawerOpen = !leftDrawerOpen" />
        <q-toolbar-title style="cursor: pointer" @click="goHome">Unimarket</q-toolbar-title>
        <q-btn v-if="!isLoggedIn" flat @click="goToLogin"> Login </q-btn>
        <q-btn v-else flat dense round icon="account_circle" @click="goToAccount" />
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
      </q-list>
    </q-drawer>

    <q-page-container>
      <q-page>
        <div class="q-px-lg q-pb-md">
          <h4>My Listings</h4>

          <!-- Show login prompt if not logged in -->
          <div v-if="!isLoggedIn" class="flex flex-center q-mt-xl">
            <q-card style="width: 100%; max-width: 400px;">
              <q-card-section class="text-center">
                <q-icon name="login" size="64px" color="primary" class="q-mb-md" />
                <h5 class="q-mt-none q-mb-sm">Login Required</h5>
                <p class="text-grey-7 q-mb-lg">
                  You need to be logged in to view your listings.
                </p>
                <q-btn
                  label="Go to Login"
                  color="primary"
                  size="lg"
                  @click="goToLogin"
                  class="full-width"
                />
              </q-card-section>
            </q-card>
          </div>

          <!-- Show listings if logged in -->
          <div v-else>
            <q-card v-for="(listing, index) in listings" :key="index" class="q-mb-md cursor-pointer" @click="goToListing(listing.id)">
              <q-card-section>
                <div v-if="listing.images && listing.images.length > 0" class="q-mb-md">
                  <!-- Image Carousel -->
                  <q-carousel
                    v-if="listing.images.length > 1"
                    v-model="imageSlides[index]"
                    swipeable
                    animated
                    arrows
                    navigation
                    height="200px"
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
                        style="height: 200px; width: 100%;"
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
                    style="height: 200px; width: 100%;"
                    class="rounded-borders"
                  />

                  <!-- Image Counter -->
                  <div v-if="listing.images.length > 1" class="absolute-top-right q-ma-sm">
                    <q-chip
                      dense
                      color="black"
                      text-color="white"
                      icon="photo"
                      :label="`${(imageSlides[index] || 0) + 1}/${listing.images.length}`"
                    />
                  </div>
                </div>
                <div class="text-h6">{{ listing.title }}</div>
                <div class="text-subtitle2">{{ "Description: " + listing.description }}</div>
                <div class="text-subtitle2">{{ "$" + listing.price + " " + listing.currency }}</div>
                <div class="text-subtitle2">{{ "Category: " + listing.category }}</div>
                <div class="text-subtitle2">{{ "Location: " + listing.location }}</div>
                <div class="text-subtitle2">{{ "Condition: " + listing.condition }}</div>
                <div class="text-subtitle2">{{ "Status: " + listing.status }}</div>
                <div class="text-subtitle2">{{ "Views: " + listing.views }}</div>
                <div class="text-subtitle2">{{ "Created at: " + formatDate(listing.created_at) + " " + getTimezoneAbbreviation() }}</div>
                <div class="text-subtitle2">{{ "Last updated: " + formatDate(listing.updated_at) + " " + getTimezoneAbbreviation() }}</div>
              </q-card-section>
              <q-card-actions align="right">
                <q-btn
                  flat
                  color="negative"
                  icon="delete"
                  label="Remove"
                  @click.stop="removeListing(listing.id, index)"
                  :loading="listing.removing"
                />
              </q-card-actions>
            </q-card>

            <!-- Show message if no listings -->
            <div v-if="listings.length === 0" class="text-center q-mt-xl">
              <q-icon name="inbox" size="64px" color="grey-5" class="q-mb-md" />
              <p class="text-grey-6">You don't have any listings yet.</p>
              <q-btn
                label="Create Your First Listing"
                color="primary"
                @click="goToAddListing"
              />
            </div>
          </div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import axios from "axios"
import { API_URL } from '../../constants.js'
import { formatDate, getTimezoneAbbreviation } from '../utils/dateUtils.js'


export default {
  name: "MyListings",
  data() {
    return {
      leftDrawerOpen: false,
      listings: [],
      imageSlides: {}, // Track current slide for each listing's carousel
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
        const token = localStorage.getItem('auth_token')
        if (!token) {
          alert('Please log in again.')
          this.$router.push('/login')
          return
        }

        const res = await axios.get(`${API_URL}listings/my_listings`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        this.listings = res.data

        // Initialize image slides for each listing
        const slides = {}
        this.listings.forEach((listing, index) => {
          slides[index] = 0 // Start at first image
        })
        this.imageSlides = slides
      } catch (e) {
        console.error("Error fetching listings:", e)
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
    async removeListing(listingId, index) {
      // Show confirmation dialog
      const confirmed = confirm('Are you sure you want to remove this listing?')
      if (!confirmed) return

      try {
        // Set loading state for this specific listing
        this.listings[index].removing = true

        const token = localStorage.getItem('auth_token')
        if (!token) {
          alert('Please log in again.')
          this.$router.push('/login')
          return
        }

        // Call API to delete listing
        await axios.delete(`${API_URL}listings/${listingId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        // Remove listing from local array
        this.listings.splice(index, 1)

        console.log('Listing removed successfully')
      } catch (error) {
        console.error('Error removing listing:', error)

        // Handle auth errors
        if (error.response?.status === 401 || error.response?.status === 403) {
          localStorage.removeItem('auth_token')
          localStorage.removeItem('user')
          this.$router.push('/login')
          return
        }

        alert('Failed to remove listing. Please try again.')
      } finally {
        // Clear loading state
        if (this.listings[index]) {
          this.listings[index].removing = false
        }
      }
    },
    goToListing(listingId) {
      this.$router.push(`/listing/${listingId}`)
    },
    formatDate,
    getTimezoneAbbreviation
  },
  mounted() {
    // Only fetch listings if user is logged in
    if (this.isLoggedIn) {
      this.getListings()             // fetch once on mount

      // Optional: Poll every 10 seconds to always show current listings
      this.polling = setInterval(() => {
        this.getListings()
      }, 10000) // 10000 = 10s
    }
  },
  beforeUnmount() {
    clearInterval(this.polling)
  }

}
</script>
