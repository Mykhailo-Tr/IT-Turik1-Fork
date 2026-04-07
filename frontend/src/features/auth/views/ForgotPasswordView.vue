<template>
  <section class="page-shell centered">
    <ui-card class="forgot-card">
      <p class="section-eyebrow">Password Recovery</p>
      <h1 class="section-title">Forgot your password?</h1>
      <p class="section-subtitle">
        Enter your account email and we will send you a password reset link.
      </p>

      <p v-if="statusMessage" :class="['notice', statusType]">{{ statusMessage }}</p>

      <form class="forgot-form" @submit.prevent="handleSubmit">
        <label class="form-label">
          Email
          <ui-input
            v-model="email"
            type="email"
            autocomplete="email"
            placeholder="name@mail.com"
            required
          />
          <small v-if="errors.email" class="text-error">{{ errors.email[0] }}</small>
        </label>

        <ui-button :disabled="isLoading" type="submit">
          {{ isLoading ? 'Sending...' : 'Send reset link' }}
        </ui-button>
      </form>

      <p class="auth-link">
        Remembered your password?
        <router-link to="/login">Back to sign in</router-link>
      </p>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiCard from '@/components/UiCard.vue'
import { useForgotPassword } from '@/queries/accounts'

const email = ref('')
const errors = ref<{ email?: string }>({})
const statusMessage = ref('')
const statusType = ref('success')

const { mutate: forgotPassword, isPending: isLoading } = useForgotPassword()

const handleSubmit = () => {
  forgotPassword(
    { body: { email: email.value } },
    {
      onSuccess: (data) => {
        statusType.value = 'success'
        statusMessage.value = data?.message || 'Password reset email sent successfully.'
      },
      onError: (err) => {
        statusType.value = 'error'
        statusMessage.value = err.response
          ? ((err.response.data as string) ?? 'Please check your email and try again.')
          : 'Server connection error.'
      },
    },
  )
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
