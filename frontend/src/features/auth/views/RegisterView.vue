<template>
  <section class="page-shell centered">
    <ui-card class="register-card">
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
            <ui-input v-model="form.username" placeholder="johndoe" required />
            <small v-if="errors?.username" class="text-error">{{ errors.username[0] }}</small>
          </label>

          <label class="form-label">
            Email
            <ui-input v-model="form.email" placeholder="name@mail.com" required />
            <small v-if="errors?.email" class="text-error">{{ errors.email[0] }}</small>
          </label>

          <label class="form-label">
            Password
            <ui-password-field
              v-model="form.password"
              autocomplete="new-password"
              placeholder="********"
              required
            />
            <small v-if="errors?.password" class="text-error">{{ errors.password[0] }}</small>
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
              class="select-control"
            />
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
            Full name
            <ui-input v-model="form.full_name" placeholder="John Doe" />
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
            <ui-input v-model="form.city" placeholder="Kyiv" />
          </label>
        </div>

        <ui-button type="submit" class="submit-btn" :disabled="isLoading">
          {{ isLoading ? 'Creating account...' : 'Create account' }}
        </ui-button>
        <p v-if="errors?.form" class="text-error text-center">{{ errors.form[0] }}</p>

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
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import GoogleAuthButton from '@/features/shared/components/auth/GoogleAuthButton.vue'
import UiPasswordField from '@/components/UiPasswordField.vue'
import PhoneField from '@/features/shared/components/forms/PhoneField.vue'
import { API_BASE } from '@/features/shared/config/api.ts'
import type { RegisterResponse } from '@/api/accounts/types'
import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiSelect from '@/components/UiSelect.vue'
import UiCard from '@/components/UiCard.vue'
import { useRegister } from '@/queries/accounts'

const router = useRouter()

const form = ref({
  username: '',
  email: '',
  password: '',
  role: 'team',
  redeem_code: '',
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

interface Errors {
  username?: string[]
  email?: string[]
  password?: string[]
  redeem_code?: string[]
  phone?: string[]
  form?: string[]
}

const errors = ref<Errors | null>(null)

const saveTokensAndRedirect = (data: RegisterResponse) => {
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

const { mutate: register, isPending: isLoading, isSuccess } = useRegister()

const handleRegister = () => {
  errors.value = null

  register(
    { body: form.value },
    {
      onError: (err) => {
        errors.value = err.response
          ? err.response.data || 'Something went wrong.'
          : { form: ['Server connection error.'] }
      },
    },
  )
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
