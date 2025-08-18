<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" @click="leftDrawerOpen = !leftDrawerOpen" />
        <q-toolbar-title>My Marketplace</q-toolbar-title>
        <q-btn flat @click="goToLogin"> Login </q-btn>
        <q-btn flat dense round icon="add" @click="goToAddListing" />
      </q-toolbar>
    </q-header>

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

    <q-page-container>
      <q-page>
        <div class="q-px-lg q-pb-md">
          <h4>Current Listings</h4>
          <q-card v-for="(listing, index) in listings" :key="index" class="q-mb-md">
            <q-card-section>
              <div v-if="listing.images && listing.images.length > 0" class="q-mb-md">
                <img :src="listing.images[0]" :alt="listing.title" style="width: 100%; max-height: 200px; object-fit: cover;" />
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
    goToLogin() {
      this.$router.push('/login')
    },
    goHome() {
      this.$router.push('/')
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
