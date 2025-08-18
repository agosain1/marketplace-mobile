<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="arrow_back" @click="goBack" />
        <q-toolbar-title>{{ isLogin ? 'Sign In' : 'Create Account' }}</q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="flex flex-center bg-grey-1 q-px-lg">
        <q-card style="width: 100%; max-width: 400px;">
          <q-card-section>

        <div v-if="errorMessage" class="q-mb-md">
          <q-banner :class="errorMessage.includes('successfully') ? 'bg-positive text-white' : 'bg-negative text-white'">
            {{ errorMessage }}
          </q-banner>
        </div>

        <q-form @submit="handleSubmit">
          <div v-if="!isLogin" class="row q-col-gutter-sm">
            <div class="col">
              <q-input
                v-model="form.firstName"
                label="First Name"
                outlined
                :rules="[val => !!val || 'First name is required']"
                name="firstName"/>
            </div>
            <div class="col">
              <q-input
                v-model="form.lastName"
                label="Last Name"
                outlined
                :rules="[val => !!val || 'Last name is required']"
                name="lastName"/>
            </div>
          </div>

          <q-input
            v-model="form.email"
            label="Email"
            type="email"
            outlined
            :rules="[
              val => !!val || 'Email is required',
              val => /.+@.+\..+/.test(val) || 'Please enter a valid email'
            ]"
            name="email"/>

          <q-input
            v-model="form.password"
            label="Password"
            :type="showPassword ? 'text' : 'password'"
            outlined
            :rules="[
              val => !!val || 'Password is required',
              val => val.length >= 6 || 'Password must be at least 6 characters'
            ]"
            name="password">
            <template v-slot:append>
              <q-icon
                :name="showPassword ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="showPassword = !showPassword"
              />
            </template>
          </q-input>

          <q-input
            v-if="!isLogin"
            v-model="form.confirmPassword"
            label="Confirm Password"
            :type="showConfirmPassword ? 'text' : 'password'"
            outlined
            :rules="[
              val => !!val || 'Please confirm your password',
              val => val === form.password || 'Passwords do not match'
            ]"
            name="confirmpwd">
            <template v-slot:append>
              <q-icon
                :name="showConfirmPassword ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="showConfirmPassword = !showConfirmPassword"
              />
            </template>
          </q-input>

          <q-btn
            type="submit"
            :label="isLogin ? 'Sign In' : 'Create Account'"
            color="primary"
            class="full-width"
            :loading="loading"
          />
        </q-form>

        <div class="text-center q-mt-md">
          <q-btn
            flat
            :label="isLogin ? 'Need an account? Sign up' : 'Already have an account? Sign in'"
            @click="toggleMode"
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
  name: "LoginPage",
  data() {
    return {
      isLogin: true,
      loading: false,
      showPassword: false,
      showConfirmPassword: false,
      errorMessage: '',
      form: {
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        confirmPassword: ''
      }
    }
  },
  methods: {
    toggleMode() {
      this.isLogin = !this.isLogin
      this.resetForm()
    },

    resetForm() {
      this.form = {
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        confirmPassword: ''
      }
      this.errorMessage = ''
    },

    async handleSubmit() {
      this.loading = true
      this.errorMessage = ''

      try {
        if (this.isLogin) {
          await this.login()
        } else {
          await this.register()
        }
      } catch (error) {
        console.error('Authentication error:', error)
        console.error('Error response:', error.response)
        console.error('Error data:', error.response?.data)
        this.errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'An error occurred'
      } finally {
        this.loading = false
      }
    },

    async login() {
      console.log('Login attempt:', { email: this.form.email, api_url: API_URL })
      const response = await axios.post(`${API_URL}auth/login`, {
        email: this.form.email,
        password: this.form.password
      })

      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        console.log('Successfully signed in!')
        this.$router.push('/')
      }
    },

    async register() {
      const response = await axios.post(`${API_URL}auth/register`, {
        fname: this.form.firstName,
        lname: this.form.lastName,
        email: this.form.email,
        password: this.form.password
      })

      if (response.data.token) {
        console.log('Account created successfully!')
        this.isLogin = true
        this.resetForm()
        // Show success message in the error banner (green styling would be better but this works)
        this.errorMessage = 'Account created successfully! Please sign in with your new credentials.'
      }
    },

    goBack() {
      this.$router.back()
    }
  }
}
</script>
