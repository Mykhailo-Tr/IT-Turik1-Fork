<template>
  <section class="page-shell centered">
    <div class="card auth-card">
      <p class="section-eyebrow">Account Access</p>
      <h1 class="section-title">Sign in to TournamentOS</h1>
      <p class="section-subtitle">
        Track your team, profile, and upcoming tournaments in one place.
      </p>

      <form @submit.prevent="handleLogin" class="auth-form">
        <label class="form-label">
          Username
          <input
            v-model="form.username"
            class="input-control"
            type="text"
            autocomplete="username"
            required
          />
        </label>

        <label class="form-label">
          Password
          <PasswordField v-model="form.password" autocomplete="current-password" required />
        </label>
        <p class="forgot-link">
          <router-link to="/forgot-password">Forgot password?</router-link>
        </p>

        <button type="submit" class="btn-primary" :disabled="isLoading">
          {{ isLoading ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>

      <p v-if="error" class="text-error feedback">{{ error }}</p>

      <GoogleAuthButton
        :api-base="API_BASE"
        divider-label="or continue with"
        @success="saveTokensAndRedirect"
      />

      <p class="auth-link">
        No account yet?
        <router-link to="/register">Create one</router-link>
      </p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import GoogleAuthButton from '@/features/shared/components/auth/GoogleAuthButton.vue'
import PasswordField from '@/features/shared/components/forms/PasswordField.vue'
import { API_BASE } from '@/features/shared/config/api.ts'
import $api from '@/services'
import type { LoginResponse } from '@/services/accounts'
import { isApiError } from '@/services/apiClient'

const form = ref({ username: '', password: '' })
const error = ref('')
const isLoading = ref(false)
const router = useRouter()

const saveTokensAndRedirect = (data: LoginResponse) => {
  localStorage.setItem('access', data.access)
  localStorage.setItem('refresh', data.refresh)
  if (data.onboarding_required) {
    localStorage.setItem('needs_onboarding', '1')
    router.push('/complete-profile')
    return
  }

  localStorage.removeItem('needs_onboarding')
  router.push('/')
}

const handleLogin = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const response = await $api.accounts.login(form.value.username, form.value.password)

    console.log('here')
    saveTokensAndRedirect(response.data)
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        error.value = 'Invalid credentials or account not activated.'
      } else {
        error.value = 'Network error. Please try again.'
      }
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.auth-card {
  width: min(100%, 520px);
  padding: 2rem;
}

.auth-form {
  display: grid;
  gap: 0.9rem;
}

.feedback {
  margin: 0.6rem 0 0;
}

.forgot-link {
  margin: -0.2rem 0 0;
  text-align: right;
  font-size: 0.9rem;
}

.forgot-link a {
  color: var(--brand-700);
  text-decoration: none;
  font-weight: 600;
}

@media (max-width: 640px) {
  .auth-card {
    padding: 1.3rem;
    border-radius: 18px;
  }
}
</style>
