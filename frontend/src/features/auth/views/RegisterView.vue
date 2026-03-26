<template>
  <section class="page-shell centered">
    <div class="card register-card">
      <p class="section-eyebrow">Join the Platform</p>
      <h1 class="section-title">Create your account</h1>
      <p class="section-subtitle">Get access to tournaments, team tools, and profile management.</p>

      <div v-if="isSuccess" class="notice success">
        Registration completed. Check <strong>{{ form.email }}</strong> to activate your account.
      </div>

      <form v-else @submit.prevent="handleRegister" class="register-form">
        <div class="form-grid">
          <label class="form-label">
            Username
            <input v-model="form.username" class="input-control" type="text" placeholder="johndoe" required />
            <small v-if="errors.username" class="text-error">{{ errors.username[0] }}</small>
          </label>

          <label class="form-label">
            Email
            <input v-model="form.email" class="input-control" type="email" placeholder="name@mail.com" required />
            <small v-if="errors.email" class="text-error">{{ errors.email[0] }}</small>
          </label>

          <label class="form-label">
            Password
            <PasswordField
              v-model="form.password"
              autocomplete="new-password"
              placeholder="********"
              required
            />
            <small v-if="errors.password" class="text-error">{{ errors.password[0] }}</small>
          </label>

          <label class="form-label">
            Role
            <select v-model="form.role" class="select-control">
              <option value="team">Team Member</option>
              <option value="organizer">Organizer</option>
              <option value="jury">Jury</option>
              <option value="admin">Admin</option>
            </select>
          </label>

          <label class="form-label full-width">
            Full name
            <input v-model="form.full_name" class="input-control" type="text" placeholder="John Doe" />
          </label>

          <label class="form-label">
            Phone
            <PhoneField v-model="form.phone" :error="errors.phone?.[0]" placeholder="Enter phone number" />
          </label>

          <label class="form-label">
            City
            <input v-model="form.city" class="input-control" type="text" placeholder="Kyiv" />
          </label>
        </div>

        <button type="submit" class="btn-primary submit-btn" :disabled="isLoading">
          {{ isLoading ? 'Creating account...' : 'Create account' }}
        </button>
        <p v-if="errors.form" class="text-error text-center">{{ errors.form[0] }}</p>

        <GoogleAuthButton
          :api-base="API_BASE"
          divider-label="or sign up with"
          @success="saveTokensAndRedirect"
        />

        <p class="auth-link">
          Already have an account?
          <router-link to="/login">Sign in</router-link>
        </p>
      </form>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import GoogleAuthButton from '@/features/shared/components/auth/GoogleAuthButton.vue'
import PasswordField from '@/features/shared/components/forms/PasswordField.vue'
import PhoneField from '@/features/shared/components/forms/PhoneField.vue'
import { API_BASE } from '@/features/shared/config/api'

const router = useRouter()

const form = ref({
  username: '',
  email: '',
  password: '',
  role: 'team',
  full_name: '',
  phone: '',
  city: '',
})

const errors = ref({})
const isLoading = ref(false)
const isSuccess = ref(false)

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

const handleRegister = async () => {
  isLoading.value = true
  errors.value = {}

  try {
    const response = await fetch(`${API_BASE}/api/accounts/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(form.value),
    })

    const data = await response.json()

    if (response.ok) {
      isSuccess.value = true
      return
    }

    errors.value = data
  } catch {
    errors.value = { form: ['Unable to connect to server.'] }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.register-card {
  width: min(100%, 720px);
  padding: 2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.full-width {
  grid-column: 1 / -1;
}

.submit-btn {
  width: 100%;
  margin-top: 1rem;
}

@media (max-width: 760px) {
  .register-card {
    padding: 1.3rem;
    border-radius: 18px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>

