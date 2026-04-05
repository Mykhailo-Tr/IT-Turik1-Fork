<template>
  <section class="page-shell centered">
    <ui-card class="complete-card">
      <p class="section-eyebrow">Final Step</p>
      <h1 class="section-title">Complete your profile</h1>
      <p class="section-subtitle">
        Choose your role and review your account details before continuing.
      </p>

      <p v-if="message" :class="['notice', messageType]">{{ message }}</p>

      <form class="form-grid" @submit.prevent="handleSubmit">
        <label class="form-label">
          Username
          <ui-input v-model="form.username" required />
          <small v-if="errors?.username" class="text-error">{{ errors.username[0] }}</small>
        </label>

        <label class="form-label">
          Role
          <ui-select
            :options="[
              { value: 'team', label: 'Team Member' },
              { value: 'organizer', label: 'Organizer' },
              { value: 'jury', label: 'Jury' },
              { value: 'admin', label: 'Admin' },
            ]"
            v-model="form.role"
            required
          />
          <small v-if="errors?.role" class="text-error">{{ errors.role[0] }}</small>
        </label>

        <label v-if="isRestrictedRole" class="form-label full-width">
          Redeem code
          <ui-input
            v-model="form.redeem_code"
            placeholder="Enter one-time activation code"
            required
          />
          <small v-if="errors?.redeem_code" class="text-error">{{ errors.redeem_code[0] }}</small>
        </label>

        <label class="form-label full-width">
          Password
          <ui-password-field
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
          <ui-input v-model="form.full_name" />
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
          <ui-input v-model="form.city" />
        </label>

        <ui-button class="submit-btn" :disabled="loading" type="submit">
          {{ loading ? 'Saving...' : 'Complete registration' }}
        </ui-button>
      </form>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import PhoneField from '@/features/shared/components/forms/PhoneField.vue'
import UiPasswordField from '@/components/UiPasswordField.vue'
import $api from '@/services'
import { isApiError } from '@/services/apiClient'
import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiSelect from '@/components/UiSelect.vue'
import UiCard from '@/components/UiCard.vue'
import { useAuth } from '@/composables/useAuth'

interface Errors {
  username?: string[]
  role?: string[]
  redeem_code?: string[]
  password?: string[]
  phone?: string[]
  form?: string[]
}

const auth = useAuth()

const router = useRouter()
const loading = ref(false)
const message = ref('')
const messageType = ref('success')
const errors = ref<Errors | null>(null)

const form = computed(() => ({
  username: auth.user.value?.username ?? '',
  role: auth.user.value?.role ?? 'team',
  redeem_code: '',
  password: '',
  full_name: auth.user.value?.full_name ?? '',
  phone: auth.user.value?.phone ?? '',
  city: auth.user.value?.city ?? '',
}))

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

  try {
    await $api.accounts.updateProfile(form.value)

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
