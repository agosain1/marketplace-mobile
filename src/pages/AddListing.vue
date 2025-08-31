<template>
  <q-layout view="lHh Lpr lFf">
    <!-- Mobile Toolbar -->
    <q-header elevated>
      <q-toolbar>
        <!-- Back Button -->
        <q-btn flat dense round icon="arrow_back" @click="goBack" />
        <q-toolbar-title>Add Listing</q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="column flex items-stretch">
        <!-- Form Content -->
        <div class="q-pa-md q-gutter-md">
      <q-input v-model="title" label="Title" filled  name="title"/>
      <q-input v-model="description" label="Description" filled type="textarea"  name="description"/>
      <q-input v-model.number="price" label="Price" type="number" filled  name="price"/>
      <q-input v-model="category" label="Category" filled  name="category"/>
      <!-- Location Section -->
      <div class="q-mb-md">
        <q-label class="q-mb-sm">Location</q-label>
        <div class="column">
          <q-btn
            @click="getCurrentLocation"
            icon="my_location"
            label="Use Current Location"
            color="primary"
            outline
            :loading="gettingLocation"
            class="q-mb-md full-width"
          />
        </div>
        <div class="q-mb-md column">
          <q-banner class="bg-positive text-white q-mb-sm" rounded>
            <template v-slot:avatar>
              <q-icon name="location_on" />
            </template>
            Location: {{ locationDisplay }}
          </q-banner>
        </div>

        <!-- Interactive Map -->
        <div class="q-mb-sm">
            <LocationMap
            :latitude="latitude"
            :longitude="longitude"
            @location-changed="onMapLocationChanged"
          />
          <div class="text-caption text-grey-6 q-mt-xs">
            Click or drag the marker to adjust the exact location
          </div>
        </div>
      </div>
      <q-select
        v-model="condition"
        :options="conditionOptions"
        label="Condition"
        filled
        emit-value
        map-options
        name="condition"
      />

      <!-- Image Upload Section -->
      <div class="q-mt-md">
        <q-label class="q-mb-sm">Images (Optional - up to 5 images, 5MB each)</q-label>
        <div class="q-mt-sm">
          <input
            ref="fileInput"
            type="file"
            multiple
            accept="image/jpeg,image/jpg,image/png,image/webp"
            style="display: none"
            @change="handleFileSelect"
          />
          <q-btn
            @click="$refs.fileInput.click()"
            icon="add_photo_alternate"
            label="Choose Images"
            color="primary"
            outline
            class="full-width"
          />
        </div>

        <!-- Image Previews -->
        <div v-if="imagePreviews.length > 0" class="q-mt-md">
          <q-label class="q-mb-sm">Image Previews:</q-label>
          <div class="row q-gutter-sm">
            <div
              v-for="(preview, index) in imagePreviews"
              :key="index"
              class="col-auto"
            >
              <q-img
                :src="preview.url"
                style="height: 100px; width: 100px"
                class="rounded-borders"
              >
                <div class="absolute-top-right">
                  <q-btn
                    flat
                    round
                    dense
                    size="sm"
                    icon="close"
                    color="white"
                    class="bg-red-6"
                    @click="removeImage(index)"
                  />
                </div>
              </q-img>
            </div>
          </div>
        </div>
      </div>

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
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted, watch } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"
import { API_URL } from '../../constants.js'
import { locationService } from '../services/locationService.js'
import LocationMap from '../components/LocationMap.vue'

const router = useRouter()

// Check authentication on mount
onMounted(() => {
  if (!localStorage.getItem('auth_token')) {
    router.push('/login')
  }
})

// state
const message = ref("")
const listings = ref([])
const title = ref("")
const description = ref("")
const price = ref(null)
const category = ref("")
const location = ref("")
const condition = ref("")
const images = ref(null)
const imagePreviews = ref([])

// Location state
const longitude = ref(-122.4194) // Default to SF coordinates
const latitude = ref(37.7749)
const manualLocation = ref("")
const locationDisplay = ref("37.7749, -122.4194") // Default coordinate display
const gettingLocation = ref(false)

// Condition options
const conditionOptions = [
  { label: 'New', value: 'new' },
  { label: 'Used', value: 'used' },
  { label: 'Refurbished', value: 'refurbished' }
]

// Watch for image file changes to generate previews
watch(images, (newImages) => {
  imagePreviews.value = []
  if (newImages) {
    const files = Array.isArray(newImages) ? newImages : [newImages]
    files.forEach((file, index) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        imagePreviews.value.push({
          url: e.target.result,
          file: file,
          index: index
        })
      }
      reader.readAsDataURL(file)
    })
  }
})

function handleFileSelect(event) {
  const files = Array.from(event.target.files)

  // Validation
  const maxFiles = 5
  const maxFileSize = 5 * 1024 * 1024 // 5MB
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']

  if (files.length > maxFiles) {
    message.value = `Maximum ${maxFiles} images allowed.`
    return
  }

  for (const file of files) {
    if (file.size > maxFileSize) {
      message.value = `Image "${file.name}" is too large. Maximum size is 5MB.`
      return
    }

    if (!allowedTypes.includes(file.type)) {
      message.value = `Image "${file.name}" format not supported. Use JPG, PNG, or WebP.`
      return
    }
  }

  // Set images and clear any previous error message
  images.value = files.length > 0 ? files : null
  message.value = ""
}

function removeImage(index) {
  imagePreviews.value.splice(index, 1)
  // Update the actual images ref
  if (images.value) {
    const files = Array.isArray(images.value) ? images.value : [images.value]
    files.splice(index, 1)
    images.value = files.length > 0 ? files : null
  }
}

async function addListing() {
  if (!title.value || !description.value || !price.value || !category.value || !latitude.value || !longitude.value || !condition.value) {
    message.value = "Please fill out all fields and allow location access"
    return
  }

  const token = localStorage.getItem('auth_token')
  if (!token) {
    message.value = "Please log in to add a listing"
    router.push('/login')
    return
  }

  try {
    message.value = "Creating listing..."

    // Use FormData for both with and without images
    const formData = new FormData()
    formData.append('title', title.value)
    formData.append('description', description.value)
    formData.append('price', price.value.toString())
    formData.append('category', category.value)
    formData.append('condition', condition.value)

    // Add GPS coordinates
    formData.append('latitude', latitude.value.toString())
    formData.append('longitude', longitude.value.toString())

    // Add image files if provided
    if (images.value && (Array.isArray(images.value) ? images.value.length > 0 : true)) {
      const files = Array.isArray(images.value) ? images.value : [images.value]
      files.forEach(file => {
        formData.append('images', file)
      })
    }

    const response = await axios.post(`${API_URL}listings`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`
      }
    })

    message.value = images.value && (Array.isArray(images.value) ? images.value.length > 0 : true)
      ? "Listing created successfully with images!"
      : "Listing created successfully!"
    console.log('Response:', response.data)

    // Reset form
    title.value = ""
    description.value = ""
    price.value = null
    category.value = ""
    location.value = ""
    condition.value = ""
    images.value = null
    imagePreviews.value = []

    // Reset location
    clearLocation()

    // Reset file input
    const fileInput = document.querySelector('input[type="file"]')
    if (fileInput) {
      fileInput.value = ""
    }

  } catch (e) {
    console.error('Error creating listing:', e)
    message.value = `Error creating listing: ${e.response?.data?.detail || e.message}`
  }
}

// Location methods
async function getCurrentLocation() {
  gettingLocation.value = true
  try {
    const position = await locationService.getCurrentPosition()
    latitude.value = position.latitude
    longitude.value = position.longitude

    message.value = ""
    locationDisplay.value = `${latitude.value.toFixed(4)}, ${longitude.value.toFixed(4)}`
  } catch (error) {
    message.value = error.message
  } finally {
    gettingLocation.value = false
  }
}

function clearLocation() {
  latitude.value = null
  longitude.value = null
  locationDisplay.value = ""
  manualLocation.value = ""
}

async function onMapLocationChanged(coordinates) {
  latitude.value = coordinates.latitude
  longitude.value = coordinates.longitude

  // Update the location display
  locationDisplay.value = `${coordinates.latitude.toFixed(4)}, ${coordinates.longitude.toFixed(4)}`
}

function goBack() {
  router.back() // 👈 goes back in history, like a phone's back button
}
</script>
