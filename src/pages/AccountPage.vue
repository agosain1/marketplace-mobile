<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="arrow_back" @click="goBack" />
        <q-toolbar-title>My Account</q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="flex flex-center bg-grey-1">
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
            color="negative"
            class="full-width"
            @click="logout"
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
    }
  }
}
</script>
