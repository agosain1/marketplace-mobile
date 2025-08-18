<template>
  <div class="fullscreen flex flex-center bg-grey-1">
    <q-card style="width: 100%; max-width: 400px;">
      <q-card-section>
        <div class="text-h6 text-center q-mb-md">
          {{ isLogin ? 'Sign In' : 'Create Account' }}
        </div>
        
        <q-form @submit="handleSubmit" class="q-gutter-md">
          <q-input
            v-if="!isLogin"
            v-model="form.name"
            label="Full Name"
            outlined
            :rules="[val => !!val || 'Name is required']"
          />
          
          <q-input
            v-model="form.email"
            label="Email"
            type="email"
            outlined
            :rules="[
              val => !!val || 'Email is required',
              val => /.+@.+\..+/.test(val) || 'Please enter a valid email'
            ]"
          />
          
          <q-input
            v-model="form.password"
            label="Password"
            :type="showPassword ? 'text' : 'password'"
            outlined
            :rules="[
              val => !!val || 'Password is required',
              val => val.length >= 6 || 'Password must be at least 6 characters'
            ]"
          >
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
          >
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
  </div>
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
      form: {
        name: '',
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
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
      }
    },
    
    async handleSubmit() {
      this.loading = true
      
      try {
        if (this.isLogin) {
          await this.login()
        } else {
          await this.register()
        }
      } catch (error) {
        console.error('Authentication error:', error)
        this.$q.notify({
          type: 'negative',
          message: error.response?.data?.message || 'An error occurred'
        })
      } finally {
        this.loading = false
      }
    },
    
    async login() {
      const response = await axios.post(`${API_URL}auth/login`, {
        email: this.form.email,
        password: this.form.password
      })
      
      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token)
        this.$q.notify({
          type: 'positive',
          message: 'Successfully signed in!'
        })
        this.$router.push('/')
      }
    },
    
    async register() {
      const response = await axios.post(`${API_URL}auth/register`, {
        name: this.form.name,
        email: this.form.email,
        password: this.form.password
      })
      
      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token)
        this.$q.notify({
          type: 'positive',
          message: 'Account created successfully!'
        })
        this.$router.push('/')
      }
    }
  }
}
</script>