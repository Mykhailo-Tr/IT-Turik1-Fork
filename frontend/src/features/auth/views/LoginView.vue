<template>
  <section class="page-shell centered">
    <ui-card class="auth-card">
      <p class="section-eyebrow">Account Access</p>
      <h1 class="section-title">Sign in to TournamentOS</h1>
      <p class="section-subtitle">
        Track your team, profile, and upcoming tournaments in one place.
      </p>

      <form @submit.prevent="handleLogin" class="auth-form">
        <label class="form-label">
          Username
          <ui-input v-model="form.username" autocomplete="username" required />
        </label>

        <label class="form-label">
          Password
          <ui-password-field v-model="form.password" autocomplete="current-password" />
        </label>
        <p class="forgot-link">
          <router-link to="/forgot-password">Forgot password?</router-link>
        </p>

        <ui-button type="submit" :disabled="isLoading">
          {{ isLoading ? 'Signing in...' : 'Sign in' }}
        </ui-button>
      </form>

      <p v-if="error" class="text-error feedback">{{ error }}</p>

      <GoogleAuthButton :api-base="API_BASE" divider-label="or continue with" @success="redirect" />

      <p class="auth-link">
        No account yet?
        <router-link to="/register">Create one</router-link>
      </p>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import GoogleAuthButton from '@/features/shared/components/auth/GoogleAuthButton.vue'
import { API_BASE } from '@/features/shared/config/api.ts'
import { isApiError } from '@/services/apiClient'
import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiPasswordField from '@/components/UiPasswordField.vue'
import UiCard from '@/components/UiCard.vue'

import { useAuth } from '@/composables/useAuth'
import type { LoginResponse } from '@/services/accounts/types'

const form = ref({ username: '', password: '' })
const error = ref('')
const isLoading = ref(false)
const router = useRouter()

const auth = useAuth()

const redirect = (data: LoginResponse) => {
  if (data.onboarding_required) {
    router.push('/complete-profile')
    return
  }

  router.push('/')
}

const handleLogin = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const data = await auth.login(form.value)

    redirect(data)
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

onMounted(() => auth.isLoggedIn && router.push('/'))
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
