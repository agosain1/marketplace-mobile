<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="arrow_back" @click="goBack" />
        <q-toolbar-title>Verify Your Email</q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="flex flex-center bg-grey-1 q-px-lg">
        <q-card style="width: 100%; max-width: 400px;">
          <q-card-section class="text-center">
            <q-icon name="email" size="64px" color="primary" class="q-mb-md" />
            <h5 class="q-mt-none q-mb-sm">Check Your Email</h5>
            <p class="text-grey-7 q-mb-lg">
              We sent a verification code to<br>
              <strong>{{ email }}</strong>
              (check spam)
            </p>

            <div v-if="errorMessage" class="q-mb-md">
              <q-banner :class="errorMessage.includes('successfully') ? 'bg-positive text-white' : 'bg-negative text-white'">
                {{ errorMessage }}
              </q-banner>
            </div>

            <q-form @submit="verifyCode">
              <q-input
                v-model="verificationCode"
                label="Enter 6-digit code"
                outlined
                maxlength="6"
                class="q-mb-md"
                :rules="[
                  val => !!val || 'Verification code is required',
                  val => val.length === 6 || 'Code must be 6 digits',
                  val => /^\d+$/.test(val) || 'Code must contain only numbers'
                ]"
                @input="onCodeInput"
              >
                <template v-slot:prepend>
                  <q-icon name="security" />
                </template>
              </q-input>

              <q-btn
                type="submit"
                label="Verify Email"
                color="primary"
                class="full-width q-mb-md"
                :loading="verifying"
                :disable="verificationCode.length !== 6"
              />
            </q-form>

            <div class="text-center">
              <p class="text-grey-6 q-mb-sm">Didn't receive the code?</p>
              <q-btn
                flat
                label="Resend Code"
                color="primary"
                @click="resendCode"
                :loading="resending"
                :disable="resendCooldown > 0"
              />
              <p v-if="resendCooldown > 0" class="text-grey-6 text-caption q-mt-sm">
                Resend available in {{ resendCooldown }}s
              </p>
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
  name: "VerifyEmailPage",
  data() {
    return {
      email: '',
      verificationCode: '',
      verifying: false,
      resending: false,
      resendCooldown: 0,
      errorMessage: '',
      cooldownTimer: null
    }
  },

  mounted() {
    // Get email from route params or localStorage
    this.email = this.$route.params.email || localStorage.getItem('pendingVerificationEmail')

    if (!this.email) {
      this.$router.push('/login')
      return
    }

    // Store email in localStorage in case user refreshes
    localStorage.setItem('pendingVerificationEmail', this.email)
  },

  beforeUnmount() {
    if (this.cooldownTimer) {
      clearInterval(this.cooldownTimer)
    }
  },

  methods: {
    onCodeInput() {
      // Auto-format to only numbers and limit to 6 digits
      this.verificationCode = this.verificationCode.replace(/\D/g, '').slice(0, 6)
    },

    async verifyCode() {
      this.verifying = true
      this.errorMessage = ''

      try {
        const response = await axios.post(`${API_URL}auth/verify-email`, {
          email: this.email,
          code: this.verificationCode
        })

        if (response.data.token) {
          // Store token and user data
          localStorage.setItem('auth_token', response.data.token)
          localStorage.setItem('user', JSON.stringify(response.data.user))

          // Clear pending verification email
          localStorage.removeItem('pendingVerificationEmail')

          this.$router.push('/')
        }
      } catch (error) {
        this.errorMessage = error.response?.data?.detail || 'Verification failed. Please try again.'
        this.verificationCode = ''
      } finally {
        this.verifying = false
      }
    },

    async resendCode() {
      this.resending = true
      this.errorMessage = ''

      try {
        await axios.post(`${API_URL}auth/resend-verification`, {
          email: this.email
        })

        this.errorMessage = 'Verification code sent successfully!'
        this.startResendCooldown()
      } catch (error) {
        this.errorMessage = error.response?.data?.detail || 'Failed to resend code. Please try again.'
      } finally {
        this.resending = false
      }
    },

    startResendCooldown() {
      this.resendCooldown = 60
      this.cooldownTimer = setInterval(() => {
        this.resendCooldown--
        if (this.resendCooldown <= 0) {
          clearInterval(this.cooldownTimer)
          this.cooldownTimer = null
        }
      }, 1000)
    },

    goBack() {
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.q-input {
  text-align: center;
}
</style>
