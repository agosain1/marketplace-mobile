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
          <h4>Current Listings</h4>
          <q-card v-for="(listing, index) in listings" :key="index" class="q-mb-md">
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
              <div class="text-subtitle2">{{ "Created at: " + listing.created_at }}</div>
              <div class="text-subtitle2">{{ "Last updated: " + listing.updated_at }}</div>

            </q-card-section>
          </q-card>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import axios from "axios"
import { API_URL } from '../../constants.js'


export default {
  name: "IndexPage",
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
        const res = await axios.get(`${API_URL}listings`)
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
    }
  },
  mounted() {
    this.getListings()             // fetch once on mount

    // Optional: Poll every 10 seconds to always show current listings
    this.polling = setInterval(() => {
      this.getListings()
    }, 10000) // 10000 = 10s
  },
  beforeUnmount() {
    clearInterval(this.polling)
  }
}
</script>
