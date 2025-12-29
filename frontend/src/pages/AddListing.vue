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
      <q-input
        v-model="title"
        label="Title"
        filled
        name="title"
        :error="validationErrors.title"
        error-message="Title is required"
        @update:model-value="clearFieldError('title')"
      />
      <q-input
        v-model="description"
        label="Description"
        filled
        type="textarea"
        name="description"
        :error="validationErrors.description"
        error-message="Description is required"
        @update:model-value="clearFieldError('description')"
      />
      <q-input
        v-model.number="price"
        label="Price"
        type="number"
        filled
        name="price"
        :error="validationErrors.price"
        error-message="Price is required"
        @update:model-value="clearFieldError('price')"
      />
      <q-input
        v-model="category"
        label="Category"
        filled
        name="category"
        :error="validationErrors.category"
        error-message="Category is required"
        @update:model-value="clearFieldError('category')"
      />
      <!-- Tags Input -->
      <q-select
        v-model="tags"
        label="Tags (optional)"
        filled
        multiple
        use-input
        use-chips
        input-debounce="0"
        new-value-mode="add-unique"
        hint="Press Enter to add tags"
        @new-value="createTag"
      >
        <template v-slot:hint>
          <div class="text-caption">Add tags like "electronics", "vintage", "negotiable"</div>
        </template>
      </q-select>
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

          <!-- Location Search with Autocomplete -->
          <div class="relative-position">
            <q-input
              v-model="locationSearch"
              label="Search city or zipcode"
              outlined
              dense
              clearable
              @keyup.enter="searchLocation"
              @update:model-value="onLocationInput"
              @focus="onInputFocus"
              @blur="hideSuggestions"
              class="q-mb-md"
            >
              <template v-slot:append>
                <q-btn
                  flat
                  round
                  dense
                  icon="search"
                  @click="searchLocation"
                  :loading="searchingLocation"
                />
              </template>
            </q-input>

            <!-- Autocomplete Suggestions -->
            <q-list
              v-if="showSuggestions && locationSuggestions.length > 0"
              class="absolute z-max bg-white shadow-4 rounded-borders"
              style="width: 100%; top: 100%; left: 0;"
            >
              <q-item
                v-for="suggestion in locationSuggestions"
                :key="suggestion.value"
                clickable
                @click="selectSuggestion(suggestion)"
                class="q-px-md q-py-sm"
              >
                <q-item-section>
                  <q-item-label>{{ suggestion.display }}</q-item-label>
                  <q-item-label caption>{{ suggestion.type === 'zipcode' ? 'Zipcode' : 'City' }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>
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
        <div class="q-mb-sm" :class="{ 'error-border': validationErrors.location }">
            <LocationMap
            :latitude="latitude"
            :longitude="longitude"
            @location-changed="onMapLocationChanged"
          />
          <div class="text-caption text-grey-6 q-mt-xs">
            Pan the map to position the marker over your desired location
          </div>
          <div v-if="validationErrors.location" class="text-negative text-caption q-mt-xs">
            Location is required
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
        :error="validationErrors.condition"
        error-message="Condition is required"
        @update:model-value="clearFieldError('condition')"
      />

      <!-- Image Upload Section -->
      <div class="q-mt-md">
        <q-label class="q-mb-sm">Images (Required - up to 5 images, 5MB each)</q-label>
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
            label="Add Images"
            color="primary"
            outline
            class="full-width"
            :class="{ 'error-border': validationErrors.images }"
          />
          <div v-if="validationErrors.images" class="text-negative text-caption q-mt-xs">
            At least one image is required
          </div>
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
      </div> <!-- ADD TAGS FORM -->

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
import { api } from 'src/boot/axios'
import { useAuth } from 'src/composables/useAuth'
import { locationService } from '../services/locationService.js'
import LocationMap from '../components/LocationMap.vue'

const router = useRouter()
const { isAuthenticated, isLoading } = useAuth()

// Watch for authentication state changes
watch(isAuthenticated, (newVal) => {
  if (!isLoading.value && !newVal) {
    router.push('/login')
  }
})

// Check authentication on mount (after loading completes)
onMounted(() => {
  if (!isLoading.value && !isAuthenticated.value) {
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
const tags = ref([])
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
const locationSearch = ref("")
const searchingLocation = ref(false)
const locationSuggestions = ref([])
const showSuggestions = ref(false)
const validationErrors = ref({})

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
  const newFiles = Array.from(event.target.files)

  // Get existing files
  const existingFiles = images.value ? (Array.isArray(images.value) ? images.value : [images.value]) : []

  // Validation
  const maxFiles = 5
  const maxFileSize = 5 * 1024 * 1024 // 5MB
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']

  // Check if total files exceed maximum
  if (existingFiles.length + newFiles.length > maxFiles) {
    message.value = `Maximum ${maxFiles} images allowed. You can add ${maxFiles - existingFiles.length} more.`
    return
  }

  for (const file of newFiles) {
    if (file.size > maxFileSize) {
      message.value = `Image "${file.name}" is too large. Maximum size is 5MB.`
      return
    }

    if (!allowedTypes.includes(file.type)) {
      message.value = `Image "${file.name}" format not supported. Use JPG, PNG, or WebP.`
      return
    }
  }

  // Combine existing and new files
  const allFiles = [...existingFiles, ...newFiles]
  images.value = allFiles.length > 0 ? allFiles : null
  message.value = ""
  clearFieldError('images')
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

function createTag(val, done) {
  // Clean and validate the tag
  const tag = val.trim().toLowerCase()
  if (tag.length > 0 && tag.length <= 30) {
    done(tag, 'add-unique')
  }
}

function validateFields() {
  validationErrors.value = {}

  if (!title.value) validationErrors.value.title = true
  if (!description.value) validationErrors.value.description = true
  if (!price.value) validationErrors.value.price = true
  if (!category.value) validationErrors.value.category = true
  if (!latitude.value || !longitude.value) validationErrors.value.location = true
  if (!condition.value) validationErrors.value.condition = true
  if (!images.value || (Array.isArray(images.value) && images.value.length === 0)) validationErrors.value.images = true

  return Object.keys(validationErrors.value).length === 0
}

function clearFieldError(field) {
  if (validationErrors.value[field]) {
    delete validationErrors.value[field]
  }
}

async function addListing() {
  if (!validateFields()) {
    message.value = "Please fill out all required fields"
    return
  }

  if (!isAuthenticated.value) {
    message.value = "Please log in to add a listing"
    router.push('/login')
    return
  }

  try {
    message.value = "Creating listing..."

    const formData = new FormData()
    formData.append('title', title.value)
    formData.append('description', description.value)
    formData.append('price', price.value.toString())
    formData.append('category', category.value)
    formData.append('condition', condition.value)

    // Add tags if any
    if (tags.value && tags.value.length > 0) {
      formData.append('tags', JSON.stringify(tags.value))
    }

    // Add GPS coordinates
    formData.append('latitude', latitude.value.toString())
    formData.append('longitude', longitude.value.toString())

    // Add image files
    if (images.value && (Array.isArray(images.value) ? images.value.length > 0 : true)) {
      const files = Array.isArray(images.value) ? images.value : [images.value]
      files.forEach(file => {
        formData.append('images', file)
      })
    }

    const response = await api.post(`listings`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    message.value = "Listing created successfully"
    console.log('Response:', response.data)

    // Reset form
    title.value = ""
    description.value = ""
    price.value = null
    category.value = ""
    tags.value = []
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

  // Clear location error when coordinates are set
  clearFieldError('location')
}

async function searchLocation() {
  if (!locationSearch.value.trim()) return

  searchingLocation.value = true

  try {
    const response = await api.get(`listings/search-location/${encodeURIComponent(locationSearch.value.trim())}`)

    if (response.data) {
      latitude.value = response.data.latitude
      longitude.value = response.data.longitude
      locationDisplay.value = response.data.place_name || `${response.data.latitude.toFixed(4)}, ${response.data.longitude.toFixed(4)}`

      message.value = ""
      locationSearch.value = ""
    }

  } catch (error) {
    console.error('Error searching location:', error)
    if (error.response?.status === 404) {
      message.value = "Location not found. Try a different search term."
    } else {
      message.value = "Failed to search location. Please try again."
    }
  } finally {
    searchingLocation.value = false
  }
}

// Autocomplete functions
let searchTimeout = null

async function onLocationInput() {
  if (searchTimeout) clearTimeout(searchTimeout)

  const query = locationSearch.value?.trim()

  if (!query || query.length < 2) {
    locationSuggestions.value = []
    showSuggestions.value = false
    return
  }

  searchTimeout = setTimeout(async () => {
    try {
      const response = await api.get(`listings/location-suggestions/${encodeURIComponent(query)}`)
      locationSuggestions.value = response.data.suggestions || []
      showSuggestions.value = locationSuggestions.value.length > 0
    } catch (error) {
      console.error('Error fetching suggestions:', error)
      locationSuggestions.value = []
      showSuggestions.value = false
    }
  }, 300)
}

function selectSuggestion(suggestion) {
  latitude.value = suggestion.latitude
  longitude.value = suggestion.longitude
  locationDisplay.value = suggestion.place_name
  locationSearch.value = ""
  locationSuggestions.value = []
  showSuggestions.value = false
  message.value = ""
}

function onInputFocus() {
  if (locationSuggestions.value.length > 0) {
    showSuggestions.value = true
  }
}

function hideSuggestions() {
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

function goBack() {
  router.back() // 👈 goes back in history, like a phone's back button
}
</script>

<style scoped>
.error-border {
  border: 2px solid #f44336;
  border-radius: 8px;
  padding: 4px;
}
</style>
