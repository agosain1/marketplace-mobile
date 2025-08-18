<template>
  <q-page padding>
        <div class="q-pa-md">
          <h4 class="q-mb-md">Current Listings</h4>
        </div>
        <div class="q-pa-md">
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
</template>

<script>
import axios from "axios"
import { API_URL } from '../../constants.js'


export default {
  name: "IndexPage",
  data() {
    return {
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
