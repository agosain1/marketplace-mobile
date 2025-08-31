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
          
          <div v-if="errorMessage" class="q-mb-md">
            <q-banner :class="errorMessage.includes('successfully') ? 'bg-positive text-white' : 'bg-negative text-white'">
              {{ errorMessage }}
            </q-banner>
          </div>

          <q-form @submit="updateProfile" v-if="editMode">
            <div class="row q-col-gutter-sm q-mb-md">
              <div class="col">
                <q-input
                  v-model="editForm.firstName"
                  label="First Name"
                  outlined
                  :rules="[val => !!val || 'First name is required']"
                  :loading="loading"
                />
              </div>
              <div class="col">
                <q-input
                  v-model="editForm.lastName"
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
                :disable="!editForm.firstName || !editForm.lastName"
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
              <strong>Name:</strong> {{ profile.firstName }} {{ profile.lastName }}
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

        <div v-else-if="user && !profile" class="text-center">
          <q-spinner-dots size="50px" color="primary" />
          <p class="q-mt-md">Loading profile...</p>
        </div>

        <div v-else class="text-center">
          <p>Please log in to view your account.</p>
          <q-btn
            label="Go to Login"
            color="primary"
            @click="goToLogin"
          />
        </div>
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import axios from "axios"
import { API_URL } from '../../constants.js'

export default {
  name: "AccountPage",
  data() {
    return {
      user: null,
      profile: null,
      editMode: false,
      loading: false,
      errorMessage: '',
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
      const userStr = localStorage.getItem('user')
      if (userStr) {
        try {
          this.user = JSON.parse(userStr)
        } catch (e) {
          console.error('Error parsing user data:', e)
          this.user = null
        }
      }
    },

    async loadProfile() {
      if (!this.user) return
      
      try {
        const token = localStorage.getItem('auth_token')
        if (!token) {
          this.goToLogin()
          return
        }

        const response = await axios.get(`${API_URL}auth/profile`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        this.profile = response.data
      } catch (error) {
        console.error('Error loading profile:', error)
        if (error.response?.status === 401) {
          this.goToLogin()
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
        const token = localStorage.getItem('auth_token')
        if (!token) {
          this.goToLogin()
          return
        }

        await axios.put(`${API_URL}auth/profile`, {
          firstName: this.editForm.firstName,
          lastName: this.editForm.lastName
        }, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
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

    logout() {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      this.$router.push('/')
    },

    goToLogin() {
      this.$router.push('/login')
    },

    goBack() {
      this.$router.back()
    },

    confirmDeleteAccount() {
      if (confirm('Are you sure you want to delete your account? This action cannot be undone and will permanently delete all your data including listings.')) {
        this.deleteAccount()
      }
    },

    async deleteAccount() {
      try {
        const token = localStorage.getItem('auth_token')
        if (!token) {
          alert('Please log in again to delete your account')
          this.$router.push('/login')
          return
        }

        await axios.delete(`${API_URL}auth/delete-account`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        alert('Your account has been successfully deleted.')
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user')
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
