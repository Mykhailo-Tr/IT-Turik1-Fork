<template>
  <section class="page-shell centered">
    <article class="card reset-card">
      <p class="section-eyebrow">Password Recovery</p>
      <h1 class="section-title">Reset password</h1>

      <p v-if="status === 'loading'" class="text-muted">Checking your reset link...</p>

      <div v-else-if="status === 'success'" class="notice success reset-success">
        {{ message }}
        <router-link class="btn-primary back-btn" to="/login">Back to Login</router-link>
      </div>

      <div v-else-if="status === 'invalid'" class="notice error">
        {{ message }}
      </div>

      <form v-else class="reset-form" @submit.prevent="handleReset">
        <label class="form-label">
          New password
          <PasswordField
            v-model="form.new_password"
            autocomplete="new-password"
            placeholder="Create a strong password"
            required
          />
          <small v-if="errors?.new_password" class="text-error">{{ errors.new_password[0] }}</small>
          <small v-else class="text-muted">
            Use at least 8 characters, including upper/lowercase letters, a number, and a special
            character.
          </small>
        </label>

        <label class="form-label">
          Confirm new password
          <PasswordField
            v-model="form.confirm_password"
            autocomplete="new-password"
            placeholder="Repeat your new password"
            required
          />
          <small v-if="errors?.confirm_password" class="text-error">{{
            errors.confirm_password[0]
          }}</small>
        </label>

        <small v-if="errors?.non_field_errors" class="text-error">{{
          errors.non_field_errors[0]
        }}</small>
        <small v-if="errors?.message" class="text-error">{{ errors.message[0] }}</small>

        <button class="btn-primary" :disabled="isLoading" type="submit">
          {{ isLoading ? 'Saving...' : 'Set new password' }}
        </button>
      </form>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import PasswordField from '@/features/shared/components/forms/PasswordField.vue'
import { API_BASE } from '@/features/shared/config/api.ts'
import $api from '@/services'
import { isApiError } from '@/services/apiClient'

interface Errors {
  new_password?: string[]
  confirm_password?: string[]
  non_field_errors?: string[]
  message: string[]
}

const route = useRoute()
const status = ref('loading')
const message = ref('')
const isLoading = ref(false)
const errors = ref<Errors | null>(null)
const form = ref({
  new_password: '',
  confirm_password: '',
})

const validateResetLink = async () => {
  try {
    await $api.accounts.resetPassword({
      type: 'validate',
      info: { uid: String(route.params.uid), token: String(route.params.token) },
    })

    status.value = 'ready'
    message.value = ''
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        errors.value = err.response.data.message || 'Password reset link is invalid or expired.'
      } else {
        message.value = 'Server connection error.'
      }
    }
    status.value = 'invalid'
  }
}

const handleReset = async () => {
  isLoading.value = true
  errors.value = null

  try {
    const response = await $api.accounts.resetPassword({
      type: 'reset',
      info: { uid: String(route.params.uid), token: String(route.params.token) },
      body: form.value,
    })

    status.value = 'success'
    message.value = response?.data.message || 'Password has been reset successfully.'
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        errors.value = err.response.data || 'Something went wrong.'
      } else {
        errors.value = { message: ['Server connection error.'] }
      }
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  validateResetLink()
})
</script>

<style scoped>
.reset-card {
  width: min(100%, 520px);
  padding: 2rem;
}

.reset-form {
  display: grid;
  gap: 0.9rem;
}

.reset-success {
  display: grid;
  gap: 0.8rem;
}

.back-btn {
  text-decoration: none;
  text-align: center;
}

@media (max-width: 640px) {
  .reset-card {
    padding: 1.3rem;
    border-radius: 18px;
  }
}
</style>
