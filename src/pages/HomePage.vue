<template>
  <q-layout view="lHh Lpr lFf">

    <!-- Top Toolbar -->
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" @click="leftDrawerOpen = !leftDrawerOpen" />
        <q-toolbar-title>My Marketplace</q-toolbar-title>
        <q-btn flat dense round icon="add" @click="goToAddListing" />
      </q-toolbar>
    </q-header>

    <!-- Side Drawer (menu) -->
    <q-drawer v-model="leftDrawerOpen" side="left" bordered>
      <q-list>
        <q-item clickable v-ripple @click="goHome">
          <q-item-section>Home</q-item-section>
        </q-item>
        <q-item clickable v-ripple>
          <q-item-section>My Listings</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <!-- Main Page -->
    <q-page-container>
      <q-page padding>
        <div class="q-pa-md">
          <q-btn color="primary" label="Add Listing" @click="goToAddListing" class="full-width" />
        </div>

        <div class="q-pa-md">
          <q-card v-for="(listing, index) in listings" :key="index" class="q-mb-md">
            <q-card-section>
              <div class="text-h6">{{ listing.title }}</div>
              <div class="text-subtitle2">{{ listing.description }}</div>
              <div class="text-subtitle2">{{ "$" + listing.price }}</div>
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
    }
  },
  methods: {
    async getListings() {
      try {
        const res = await axios.get(`${API_URL}listings`)
        this.listings = res.data
      } catch (e) {
        console.error("Error fetching listings:", e)
      }
    },
    goToAddListing() {
      this.$router.push("/add")
    },
    goHome() {
      this.$router.push("/")
    }
  },
  mounted() {
    this.getListings()             // fetch once on mount

    // Optional: Poll every 10 seconds to always show current listings
    this.polling = setInterval(() => {
      this.getListings()
    }, 10000000) // 10000 = 10s
  },
  beforeUnmount() {
    clearInterval(this.polling)
  }
}
</script>
