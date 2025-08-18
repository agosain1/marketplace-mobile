<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="arrow_back" @click="goBack" />
        <q-toolbar-title>My Account</q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="flex flex-center bg-grey-1 q-px-lg q-col-gutter-md">
        <q-card style="width: 100%; max-width: 400px;">
          <q-card-section>

        <div v-if="user" class="q-gutter-md">
          <div class="text-subtitle1">
            <strong>Email:</strong> {{ user.email }}
          </div>
          <div class="text-subtitle1">
            <strong>User ID:</strong> {{ user.id }}
          </div>

          <q-separator class="q-my-md" />

          <q-btn
            label="Logout"
            color="primary"
            class="full-width q-mb-sm"
            @click="logout"
          />

          <q-btn
            label="Delete My Account"
            color="negative"
            outline
            class="full-width"
            @click="confirmDeleteAccount"
          />
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
      user: null
    }
  },
  mounted() {
    this.loadUser()
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
