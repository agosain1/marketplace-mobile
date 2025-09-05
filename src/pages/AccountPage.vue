<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="arrow_back" @click="goBack" />
        <q-toolbar-title>My Account</q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="flex flex-center bg-grey-1 q-px-lg">
        <q-card style="width: 100%; max-width: 500px;">
          <q-card-section>

        <div v-if="user && profile" class="q-gutter-md">
          <!-- Profile Section -->
          <div class="text-h6 q-mb-md">Profile Information</div>

          <q-img
                      :src="profile.pfp_url"
                      :alt="`could not load pfp`"
                      fit="cover"
                      style="height: 30px; width: 10%;"
                      class="rounded-borders"
                    />

          <!-- Image Upload Button -->
          <q-btn
            label="Upload Profile Picture"
            color="primary"
            icon="upload"
            @click="triggerFileUpload"
            :loading="uploadingImage"
            class="q-mb-md"
          />
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            style="display: none"
            @change="handleImageUpload"
          />



          <div v-if="errorMessage" class="q-mb-md">
            <q-banner :class="errorMessage.includes('successfully') ? 'bg-positive text-white' : 'bg-negative text-white'">
              {{ errorMessage }}
            </q-banner>
          </div>

          <q-form @submit="updateProfile" v-if="editMode">
            <div class="row q-col-gutter-sm q-mb-md">
              <div class="col">
                <q-input
                  v-model="editForm.fname"
                  label="First Name"
                  outlined
                  :rules="[val => !!val || 'First name is required']"
                  :loading="loading"
                />
              </div>
              <div class="col">
                <q-input
                  v-model="editForm.lname"
                  label="Last Name"
                  outlined
                  :rules="[val => !!val || 'Last name is required']"
                  :loading="loading"
                />
              </div>
            </div>

            <div class="row q-gutter-sm">
              <q-btn
                type="submit"
                color="positive"
                icon="save"
                :loading="loading"
                :disable="!editForm.fname || !editForm.lname"
              >
                Save Changes
              </q-btn>
              <q-btn
                color="grey"
                outline
                icon="cancel"
                @click="cancelEdit"
                :disable="loading"
              >
                Cancel
              </q-btn>
            </div>
          </q-form>

          <div v-else>
            <div class="q-mb-sm">
              <strong>Name:</strong> {{ profile.fname }} {{ profile.lname }}
              <q-btn
                flat
                dense
                round
                icon="edit"
                size="sm"
                class="q-ml-sm"
                @click="startEdit"
                color="primary"
              />
            </div>
            <div class="q-mb-sm">
              <strong>Email:</strong> {{ profile.email }}
              <q-chip
                v-if="profile.isGoogleUser"
                size="sm"
                color="blue"
                text-color="white"
                icon="account_circle"
                class="q-ml-sm"
              >
                Google Account
              </q-chip>
            </div>
            <div class="text-subtitle1 text-grey-6">
              <strong>User ID:</strong> {{ user.id }}
            </div>
          </div>

          <q-separator class="q-my-lg" />

          <!-- Actions Section -->
          <div class="text-h6 q-mb-md">Account Actions</div>

          <q-btn
            label="Logout"
            color="primary"
            class="full-width q-mb-sm"
            icon="logout"
            @click="logout"
          />

          <q-btn
            label="Delete My Account"
            color="negative"
            outline
            class="full-width"
            icon="delete_forever"
            @click="confirmDeleteAccount"
          />
        </div>

        <div v-else-if="!user" class="flex flex-center">
          <q-card style="width: 100%; max-width: 400px;">
            <q-card-section class="text-center">
              <q-icon name="login" size="64px" color="primary" class="q-mb-md" />
              <h5 class="q-mt-none q-mb-sm">Login Required</h5>
              <p class="text-grey-7 q-mb-lg">
                You must be logged in to view your account.
              </p>
              <q-btn
                label="Go to Login"
                color="primary"
                @click="goToLogin"
                class="full-width"
              />
            </q-card-section>
          </q-card>
        </div>

        <div v-else class="text-center">
          <q-spinner-dots size="50px" color="primary" />
          <p class="q-mt-md">Loading profile...</p>
        </div>
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import { api } from 'src/boot/axios'
import { useAuthStore } from 'stores/authStore.js'

export default {
  name: "AccountPage",
  data() {
    return {
      user: null,
      profile: null,
      editMode: false,
      loading: false,
      errorMessage: '',
      uploadingImage: false,
      editForm: {
        firstName: '',
        lastName: ''
      }
    }
  },
  mounted() {
    this.loadUser()
    if (this.user) {
      this.loadProfile()
    }
  },
  methods: {
    loadUser() {
      const authStore = useAuthStore()
      this.user = authStore.user
    },

    async loadProfile() {
      if (!this.user) return

      try {
        const response = await api.get(`account/profile`)
        this.profile = response.data.user
        console.log(this.profile)
        this.profile.isGoogleUser = this.profile.google_id !== null
        if (!this.profile.pfp_url || this.profile.pfp_url.length === 0) {
          this.profile.pfp_url = 'https://toppng.com/uploads/preview/instagram-default-profile-picture-11562973083brycehrmyv.png' // DEFAULT URL
        }
      } catch (error) {
        console.error('Error loading profile:', error)
        if (error.response?.status === 401) {
          console.log('User not authenticated - clearing user data')
        } else {
          this.errorMessage = 'Failed to load profile information'
        }
      }
    },

    startEdit() {
      this.editMode = true
      this.editForm.firstName = this.profile.firstName
      this.editForm.lastName = this.profile.lastName
      this.errorMessage = ''
    },

    cancelEdit() {
      this.editMode = false
      this.editForm.firstName = ''
      this.editForm.lastName = ''
      this.errorMessage = ''
    },

    async updateProfile() {
      this.loading = true
      this.errorMessage = ''

      try {
        await api.put(`account/profile`, {
          firstName: this.editForm.firstName,
          lastName: this.editForm.lastName
        })

        // Update profile data
        this.profile.firstName = this.editForm.firstName
        this.profile.lastName = this.editForm.lastName

        this.editMode = false
        this.errorMessage = 'Profile updated successfully!'

        // Clear success message after 3 seconds
        setTimeout(() => {
          this.errorMessage = ''
        }, 3000)

      } catch (error) {
        console.error('Error updating profile:', error)
        this.errorMessage = error.response?.data?.detail || 'Failed to update profile'
      } finally {
        this.loading = false
      }
    },

    async logout() {
      await api.post(`auth/logout`)
      const authStore = useAuthStore()
      authStore.clearAuth()
      this.$router.push('/')
    },

    goToLogin() {
      this.$router.push('/login')
    },

    goBack() {
      this.$router.back()
    },

    triggerFileUpload() {
      this.$refs.fileInput.click()
    },

    async handleImageUpload(event) {
      const file = event.target.files[0]
      if (!file) return

      this.uploadingImage = true
      this.errorMessage = ''

      try {
        const formData = new FormData()
        formData.append('image', file)

        const response = await api.put('account/upload_pfp', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        // Update profile with new image URL
        if (response.data.pfp_url) {
          this.profile.pfp_url = response.data.pfp_url
          this.errorMessage = 'Profile picture updated successfully!'

          // Clear success message after 3 seconds
          setTimeout(() => {
            this.errorMessage = ''
          }, 3000)
        }

      } catch (error) {
        console.error('Error uploading image:', error)
        this.errorMessage = error.response?.data?.detail || 'Failed to upload image'
      } finally {
        this.uploadingImage = false
        // Clear the file input
        event.target.value = ''
      }
    },

    confirmDeleteAccount() {
      if (confirm('Are you sure you want to delete your account? This action cannot be undone and will permanently delete all your data including listings.')) {
        this.deleteAccount()
      }
    },

    async deleteAccount() {
      try {
        await api.delete(`account/delete-account`)

        alert('Your account has been successfully deleted.')
        const authStore = useAuthStore()
        authStore.clearAuth()
        this.$router.push('/')

      } catch (e) {
        console.error('Error deleting account:', e)
        const errorMessage = e.response?.data?.detail || e.message || 'An error occurred while deleting your account. Please try again.'
        alert('Error deleting account: ' + errorMessage)
      }
    }
  }
}
</script>
