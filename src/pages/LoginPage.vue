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
            :rules="passwordValidationRules"
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

        <!-- Divider -->
        <div class="row items-center q-my-lg">
          <div class="col">
            <q-separator />
          </div>
          <div class="col-auto q-px-md text-grey-6">
            OR
          </div>
          <div class="col">
            <q-separator />
          </div>
        </div>

        <!-- Google Sign-In -->
        <GoogleSignIn
          @success="handleGoogleSignInSuccess"
          @error="handleGoogleSignInError"
        />

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
import { api } from 'src/boot/axios'
import GoogleSignIn from '../components/GoogleSignIn.vue'

export default {
  name: "LoginPage",
  components: {
    GoogleSignIn
  },
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
  computed: {
    passwordValidationRules() {
      return [
        val => !!val || 'Password is required',
        val => val.length >= 8 || 'Password must be at least 8 characters',
        val => /[A-Z]/.test(val) || 'Password must contain at least one uppercase letter',
        val => /[a-z]/.test(val) || 'Password must contain at least one lowercase letter',
        val => /[0-9]/.test(val) || 'Password must contain at least one number',
        val => this.hasSpecialCharacter(val) || 'Password must contain at least one special character'
      ]
    }
  },
  methods: {
    hasSpecialCharacter(password) {
      // Define special characters safely without escaping issues
      const specialChars = '!@#$%^&*(),.?":{}|<>'
      return specialChars.split('').some(char => password.includes(char))
    },
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
      try {
        const response = await api.post(`auth/login`, {
          email: this.form.email,
          password: this.form.password
        })

        if (response.data.token) {
          localStorage.setItem('auth_token', response.data.token)
          localStorage.setItem('user', JSON.stringify(response.data.user))
          console.log('Successfully signed in!')
          this.$router.push('/')
        }
      } catch (error) {
        // Check if this is an email verification error
        if (error.response?.status === 403 &&
            error.response?.data?.detail?.includes('Email not verified')) {

          // Get email from response header or use form email
          const email = error.response.headers['x-verification-email'] || this.form.email

          console.log('Email not verified, redirecting to verification page')
          this.$router.push(`/verify-email/${encodeURIComponent(email)}`)
          return // Don't re-throw the error since we're handling it
        }

        // Re-throw other errors to be handled by the main error handler
        throw error
      }
    },

    async register() {
      const response = await api.post(`auth/register`, {
        fname: this.form.firstName,
        lname: this.form.lastName,
        email: this.form.email,
        password: this.form.password
      })

      if (response.data.message && response.data.email) {
        console.log('Account created successfully! Redirecting to verification page.')
        // Redirect to verification page with email
        this.$router.push(`/verify-email/${encodeURIComponent(response.data.email)}`)
      }
    },

    goBack() {
      this.$router.back()
    },

    async handleGoogleSignInSuccess(googleData) {
      this.loading = true
      this.errorMessage = ''

      try {
        console.log('Google Sign-In successful:', googleData)

        // Send the Google ID token to our backend
        const response = await api.post(`auth/google`, {
          idToken: googleData.idToken,
          profile: googleData.profile
        })

        if (response.data.token) {
          localStorage.setItem('auth_token', response.data.token)
          localStorage.setItem('user', JSON.stringify(response.data.user))
          console.log('Successfully signed in with Google!')
          this.$router.push('/')
        }
      } catch (error) {
        console.error('Google authentication error:', error)
        this.errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Google Sign-In failed'
      } finally {
        this.loading = false
      }
    },

    handleGoogleSignInError(error) {
      console.error('Google Sign-In error:', error)
      this.errorMessage = `Google Sign-In failed: ${error}`
    }
  }
}
</script>
