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
      <q-input v-model="location" label="Location" filled  name="location"/>
      
      <!-- Image Upload Section -->
      <div class="q-mt-md">
        <q-label class="q-mb-sm">Images (Optional - up to 5 images, 5MB each)</q-label>
        <q-file 
          v-model="images" 
          multiple 
          accept="image/jpeg,image/jpg,image/png,image/webp"
          max-files="5"
          max-file-size="5242880"
          filled
          counter
          @rejected="onImageRejected"
        >
          <template v-slot:prepend>
            <q-icon name="attach_file" />
          </template>
        </q-file>
        
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
const location = ref ("")
const images = ref(null)
const imagePreviews = ref([])
//const condition = ref("")
//const status = ref("")

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

function onImageRejected(rejectedEntries) {
  rejectedEntries.forEach(entry => {
    if (entry.failedPropValidation === 'max-file-size') {
      message.value = `Image "${entry.file.name}" is too large. Maximum size is 5MB.`
    } else if (entry.failedPropValidation === 'accept') {
      message.value = `Image "${entry.file.name}" format not supported. Use JPG, PNG, or WebP.`
    } else if (entry.failedPropValidation === 'max-files') {
      message.value = 'Maximum 5 images allowed.'
    }
  })
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
  if (!title.value || !description.value || !price.value || !category.value || !location.value ) {
    message.value = "Please fill out all fields"
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
    
    // Determine which endpoint to use based on whether images are provided
    const hasImages = images.value && (Array.isArray(images.value) ? images.value.length > 0 : true)
    
    if (hasImages) {
      // Use FormData for file upload
      const formData = new FormData()
      formData.append('title', title.value)
      formData.append('description', description.value)
      formData.append('price', price.value.toString())
      formData.append('category', category.value)
      formData.append('location', location.value)
      
      // Add image files
      const files = Array.isArray(images.value) ? images.value : [images.value]
      files.forEach(file => {
        formData.append('images', file)
      })

      const response = await axios.post(`${API_URL}listings/with-images`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        }
      })
      
      message.value = "Listing created successfully with images!"
      console.log('Response:', response.data)
    } else {
      // Use regular JSON endpoint for listings without images
      const userStr = localStorage.getItem('user')
      const user = JSON.parse(userStr)
      
      const listingData = {
        title: title.value,
        description: description.value,
        price: price.value,
        category: category.value,
        location: location.value,
        seller_id: user.id
      }
      
      await axios.post(`${API_URL}listings`, listingData)
      message.value = "Listing created successfully!"
    }
    
    // Reset form
    title.value = ""
    description.value = ""
    price.value = null
    category.value = ""
    location.value = ""
    images.value = null
    imagePreviews.value = []
    
  } catch (e) {
    console.error('Error creating listing:', e)
    message.value = `Error creating listing: ${e.response?.data?.detail || e.message}`
  }
}

function goBack() {
  router.back() // 👈 goes back in history, like a phone's back button
}
</script>
