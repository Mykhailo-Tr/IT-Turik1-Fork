<template>
  <section class="page-shell centered">
    <article class="card complete-card">
      <p class="section-eyebrow">Final Step</p>
      <h1 class="section-title">Complete your profile</h1>
      <p class="section-subtitle">
        Choose your role and review your account details before continuing.
      </p>

      <p v-if="message" :class="['notice', messageType]">{{ message }}</p>

      <form class="form-grid" @submit.prevent="handleSubmit">
        <label class="form-label">
          Username
          <input v-model="form.username" class="input-control" type="text" required />
          <small v-if="errors?.username" class="text-error">{{ errors.username[0] }}</small>
        </label>

        <label class="form-label">
          Role
          <select v-model="form.role" class="select-control" required>
            <option value="" disabled>Select role</option>
            <option value="team">Team Member</option>
            <option value="organizer">Organizer</option>
            <option value="jury">Jury</option>
            <option value="admin">Admin</option>
          </select>
          <small v-if="errors?.role" class="text-error">{{ errors.role[0] }}</small>
        </label>

        <label v-if="isRestrictedRole" class="form-label full-width">
          Redeem code
          <input
            v-model="form.redeem_code"
            class="input-control"
            type="text"
            placeholder="Enter one-time activation code"
            required
          />
          <small v-if="errors?.redeem_code" class="text-error">{{ errors.redeem_code[0] }}</small>
        </label>

        <label class="form-label full-width">
          Password
          <PasswordField
            v-model="form.password"
            autocomplete="new-password"
            placeholder="Create a strong password"
            required
          />
          <small v-if="errors?.password" class="text-error">{{ errors.password[0] }}</small>
          <small v-else class="field-help">
            Use at least 8 characters, including upper/lowercase letters, a number, and a special
            character.
          </small>
        </label>

        <label class="form-label full-width">
          Full name
          <input v-model="form.full_name" class="input-control" type="text" />
        </label>

        <label class="form-label">
          Phone
          <PhoneField
            v-model="form.phone"
            :error="errors?.phone?.[0]"
            placeholder="Enter phone number"
          />
        </label>

        <label class="form-label">
          City
          <input v-model="form.city" class="input-control" type="text" />
        </label>

        <button class="btn-primary submit-btn" :disabled="loading || bootLoading" type="submit">
          {{ loading ? 'Saving...' : 'Complete registration' }}
        </button>
      </form>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import PhoneField from '@/features/shared/components/forms/PhoneField.vue'
import PasswordField from '@/features/shared/components/forms/PasswordField.vue'
import $api from '@/services'
import { isApiError } from '@/services/apiClient'

interface Errors {
  username?: string[]
  role?: string[]
  redeem_code?: string[]
  password?: string[]
  phone?: string[]
  form?: string[]
}

const router = useRouter()
const loading = ref(false)
const bootLoading = ref(true)
const message = ref('')
const messageType = ref('success')
const errors = ref<Errors | null>(null)

const form = ref({
  username: '',
  role: '',
  redeem_code: '',
  password: '',
  full_name: '',
  phone: '',
  city: '',
})

const restrictedRoles = ['jury', 'organizer', 'admin']
const isRestrictedRole = computed(() => restrictedRoles.includes(form.value.role))

watch(
  () => form.value.role,
  (newRole) => {
    if (!restrictedRoles.includes(newRole)) {
      form.value.redeem_code = ''
    }
  },
)

const getPasswordError = (password: string) => {
  if (!password) return 'Password is required to complete registration.'
  if (password.length < 8) return 'Password must be at least 8 characters long.'
  if (!/[A-Z]/.test(password)) return 'Password must include at least one uppercase letter.'
  if (!/[a-z]/.test(password)) return 'Password must include at least one lowercase letter.'
  if (!/\d/.test(password)) return 'Password must include at least one digit.'
  if (!/[^A-Za-z0-9]/.test(password)) return 'Password must include at least one special character.'
  return null
}

// TODO: Remove
// const logoutToLogin = () => {
//   localStorage.removeItem('access')
//   localStorage.removeItem('refresh')
//   localStorage.removeItem('needs_onboarding')
//   router.push('/login')
// }

const handleSubmit = async () => {
  loading.value = true
  errors.value = {}
  message.value = ''

  const passwordError = getPasswordError(form.value.password)
  if (passwordError) {
    errors.value = { password: [passwordError] }
    messageType.value = 'error'
    message.value = 'Please fix form errors and try again.'
    loading.value = false
    return
  }

  const token = localStorage.getItem('access')

  if (!token) {
    router.push('/login')
    return
  }

  try {
    await $api.accounts.updateProfile(token, form.value)

    localStorage.removeItem('needs_onboarding')
    messageType.value = 'success'
    message.value = 'Profile completed successfully.'
    router.push('/')
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        if (err.response.status === 401) return router.push('/login')

        errors.value = err.response.data
        messageType.value = 'error'
        message.value = 'Please fix form errors and try again.'
      } else {
        messageType.value = 'error'
        message.value = 'Server connection error.'
      }
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const token = localStorage.getItem('access')
  if (!token) {
    router.push('/login')
    return
  }

  try {
    const response = await $api.accounts.getProfile(token)

    if (!response.data.needs_onboarding) {
      localStorage.removeItem('needs_onboarding')
      router.push('/')
      return
    }

    form.value = {
      username: response.data.username || '',
      role: '',
      redeem_code: '',
      password: '',
      full_name: response.data.full_name || '',
      phone: response.data.phone || '',
      city: response.data.city || '',
    }
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        if (err.response.status === 401) return router.push('/login')
        messageType.value = 'error'
        message.value = 'Could not load your profile.'
      } else {
        messageType.value = 'error'
        message.value = 'Server connection error.'
      }
    }
  } finally {
    bootLoading.value = false
  }
})
</script>

<style scoped>
.complete-card {
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
  margin-top: 0.5rem;
  grid-column: 1 / -1;
}

.field-help {
  color: var(--text-muted);
}

@media (max-width: 760px) {
  .complete-card {
    padding: 1.3rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .submit-btn {
    grid-column: auto;
  }
}
</style>
