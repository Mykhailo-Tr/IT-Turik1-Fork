<template>
  <section class="page-shell centered">
    <article class="card forgot-card">
      <p class="section-eyebrow">Password Recovery</p>
      <h1 class="section-title">Forgot your password?</h1>
      <p class="section-subtitle">Enter your account email and we will send you a password reset link.</p>

      <p v-if="statusMessage" :class="['notice', statusType]">{{ statusMessage }}</p>

      <form class="forgot-form" @submit.prevent="handleSubmit">
        <label class="form-label">
          Email
          <input
            v-model="email"
            class="input-control"
            type="email"
            autocomplete="email"
            placeholder="name@mail.com"
            required
          />
          <small v-if="errors.email" class="text-error">{{ errors.email[0] }}</small>
        </label>

        <button class="btn-primary" :disabled="isLoading" type="submit">
          {{ isLoading ? 'Sending...' : 'Send reset link' }}
        </button>
      </form>

      <p class="auth-link">
        Remembered your password?
        <router-link to="/login">Back to sign in</router-link>
      </p>
    </article>
  </section>
</template>

<script setup>
import { ref } from 'vue'

import { API_BASE } from '@/features/shared/config/api'

const email = ref('')
const isLoading = ref(false)
const errors = ref({})
const statusMessage = ref('')
const statusType = ref('success')

const handleSubmit = async () => {
  isLoading.value = true
  errors.value = {}
  statusMessage.value = ''

  try {
    const response = await fetch(`${API_BASE}/api/accounts/password-reset/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value }),
    })

    const data = await response.json()

    if (!response.ok) {
      errors.value = data
      statusType.value = 'error'
      statusMessage.value = data.detail || 'Please check your email and try again.'
      return
    }

    statusType.value = 'success'
    statusMessage.value = data.message || 'Password reset email sent successfully.'
  } catch {
    statusType.value = 'error'
    statusMessage.value = 'Server connection error.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.forgot-card {
  width: min(100%, 520px);
  padding: 2rem;
}

.forgot-form {
  display: grid;
  gap: 0.9rem;
}

@media (max-width: 640px) {
  .forgot-card {
    padding: 1.3rem;
    border-radius: 18px;
  }
}
</style>
