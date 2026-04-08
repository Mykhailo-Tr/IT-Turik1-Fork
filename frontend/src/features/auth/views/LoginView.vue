<template>
  <section class="page-shell centered">
    <ui-card class="auth-card">
      <template #header>
        <p class="section-eyebrow">Account Access</p>
        <h1 class="section-title">Sign in to TournamentOS</h1>
        <p class="section-subtitle">
          Track your team, profile, and upcoming tournaments in one place.
        </p>
      </template>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-item">
          <label class="form-label"> Username </label>
          <ui-input v-model="form.username" autocomplete="username" required />
        </div>

        <div class="form-item">
          <label class="form-label"> Password </label>
          <ui-password-field v-model="form.password" autocomplete="current-password" />
        </div>

        <p class="forgot-link">
          <router-link to="/forgot-password">Forgot password?</router-link>
        </p>

        <ui-button type="submit" :disabled="isPending">
          {{ isPending ? 'Signing in...' : 'Sign in' }}
        </ui-button>
      </form>

      <p v-if="error" class="text-error feedback">{{ error }}</p>

      <GoogleAuthButton divider-label="or continue with" @success="saveAndRedirect" />

      <template #footer>
        <p class="auth-link">
          No account yet?
          <router-link to="/register">Create one</router-link>
        </p>
      </template>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import GoogleAuthButton from '@/features/shared/components/auth/GoogleAuthButton.vue'
import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiPasswordField from '@/components/UiPasswordField.vue'
import UiCard from '@/components/UiCard.vue'
import { useUserStore } from '@/stores/user'
import { useLogin } from '@/queries/accounts'
import { useQueryClient } from '@tanstack/vue-query'
import { accountKeys } from '@/queries/keys'
import type { LoginResponse } from '@/api/accounts/types'

const queryClient = useQueryClient()
const store = useUserStore()

const form = ref({ username: '', password: '' })
const error = ref('')
const router = useRouter()

const saveAndRedirect = (data: LoginResponse) => {
  store.setTokens(data)
  router.push('/')
}

const { mutate: login, isPending } = useLogin()

const handleLogin = async () => {
  login(
    { body: form.value },
    {
      onSuccess: (data) => {
        saveAndRedirect(data)
        queryClient.invalidateQueries({ queryKey: accountKeys.profile() })
      },
      onError: (err) => {
        if (err.response) {
          error.value = 'Invalid credentials or account not activated.'
        } else {
          error.value = 'Network error. Please try again.'
        }
      },
    },
  )
}
// We do this to reset AppNavbar state
// Like if we get 401 error and redirected to login
// We need to refetch profile to show Login and Register buttons
onMounted(() => queryClient.resetQueries({ queryKey: accountKeys.profile() }))
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

.form-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
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
