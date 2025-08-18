<template>
  <q-page class="column flex items-stretch">
    <!-- Mobile Toolbar -->
    <q-header elevated>
      <q-toolbar>
        <!-- Back Button -->
        <q-btn flat dense round icon="arrow_back" @click="goBack" />
        <q-toolbar-title>Add Listing</q-toolbar-title>
      </q-toolbar>
    </q-header>

    <!-- Form Content -->
    <div class="q-pa-md q-gutter-md">
      <q-input v-model="title" label="Title" filled />
      <q-input v-model="description" label="Description" filled type="textarea" />
      <q-input v-model.number="price" label="Price" type="number" filled />
      <q-input v-model="category" label="Category" filled />
      <q-input v-model="location" label="Location" filled />
      <!-- <q-input v-model="condition" label="Condition" filled />-->
      <!-- <q-input v-model="status" label="Status" filled /> -->

      <q-btn label="Add Listing" color="secondary" class="full-width" @click="addListing" />
    </div>

    <!-- Feedback message -->
    <div class="q-pa-md">
      <p v-if="message"><strong>{{ message }}</strong></p>
      <ul>
        <li v-for="(listing, idx) in listings" :key="idx">
          {{ listing.title }} - ${{ listing.price }}
        </li>
      </ul>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"
import { API_URL } from '../../constants.js'

const router = useRouter()

// state
const message = ref("")
const listings = ref([])
const title = ref("")
const description = ref("")
const price = ref(null)
const category = ref("")
const location = ref ("")
//const condition = ref("")
//const status = ref("")

async function addListing() {
  if (!title.value || !description.value || !price.value || !category.value || !location.value ) { // || !condition.value || !status.value) {
    message.value = "Please fill out all fields"
    return
  }

  try {
    await axios.post(`${API_URL}listings`, {
      title: title.value,
      description: description.value,
      price: price.value,
      category: category.value,
      location: location.value,
      //condition: condition.value,
      //status: status.value
    })
    message.value = "Listing added!"
    listings.value.push({
      title: title.value,
      description: description.value,
      price: price.value,
      category: category.value,
      location: location.value,
      //condition: condition.value,
      //status: status.value
    })
    // reset form
    title.value = ""
    description.value = ""
    price.value = null
    category.value = ""
    location.value = ""
    //condition.value = ""
    //status.value = ""
  } catch (e) {
    message.value = "Error adding listing: " + e.message
  }
}

function goBack() {
  router.back() // 👈 goes back in history, like a phone's back button
}
</script>
