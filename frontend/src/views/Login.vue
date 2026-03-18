<template>
  <section class="page-shell centered">
    <div class="card auth-card">
      <p class="section-eyebrow">Account Access</p>
      <h1 class="section-title">Sign in to TournamentOS</h1>
      <p class="section-subtitle">Track your team, profile, and upcoming tournaments in one place.</p>

      <form @submit.prevent="handleLogin" class="auth-form">
        <label class="form-label">
          Username
          <input v-model="form.username" class="input-control" type="text" autocomplete="username" required />
        </label>

        <label class="form-label">
          Password
          <input v-model="form.password" class="input-control" type="password" autocomplete="current-password" required />
        </label>

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

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import GoogleAuthButton from '@/components/auth/GoogleAuthButton.vue'
import { API_BASE } from '@/config/api'

const form = ref({ username: '', password: '' })
const error = ref('')
const isLoading = ref(false)
const router = useRouter()

const saveTokensAndRedirect = (data) => {
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
    const response = await fetch(`${API_BASE}/api/accounts/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })

    const data = await response.json()

    if (response.ok) {
      saveTokensAndRedirect(data)
      return
    }

    error.value = 'Invalid credentials or account not activated.'
  } catch {
    error.value = 'Network error. Please try again.'
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

@media (max-width: 640px) {
  .auth-card {
    padding: 1.3rem;
    border-radius: 18px;
  }
}
</style>
