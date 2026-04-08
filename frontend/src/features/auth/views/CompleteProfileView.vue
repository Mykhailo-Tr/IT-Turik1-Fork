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
        <div class="form-item">
          <label class="form-label"> Username </label>
          <ui-input v-model="form.username" required />
          <small v-if="errors?.username" class="text-error">{{ errors.username[0] }}</small>
        </div>

        <div class="form-item">
          <label class="form-label"> Role </label>
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
        </div>

        <div>
          <div class="form-item" v-if="isRestrictedRole">
            <label class="form-label full-width"> Redeem code </label>
            <ui-input
              v-model="form.redeem_code"
              placeholder="Enter one-time activation code"
              required
            />
            <small v-if="errors?.redeem_code" class="text-error">{{ errors.redeem_code[0] }}</small>
          </div>

          <div class="form-item">
            <label class="form-label full-width"> Password </label>
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
          </div>
        </div>

        <div class="form-item">
          <label class="form-label full-width"> Full name </label>
          <ui-input v-model="form.full_name" />
        </div>

        <div class="form-item">
          <label class="form-label"> Phone </label>
          <PhoneField
            v-model="form.phone"
            :error="errors?.phone?.[0]"
            placeholder="Enter phone number"
          />
        </div>

        <div class="form-item">
          <label class="form-label"> City </label>
          <ui-input v-model="form.city" />
        </div>

        <ui-button class="submit-btn" :disabled="isUpdatingProfile" type="submit">
          <loading-icon v-if="isUpdatingProfile" />
          Complete registration
        </ui-button>
      </form>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import PhoneField from '@/features/shared/components/forms/PhoneField.vue'
import UiPasswordField from '@/components/UiPasswordField.vue'
import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiSelect from '@/components/UiSelect.vue'
import UiCard from '@/components/UiCard.vue'
import { useProfile, useUpdateProfile } from '@/queries/accounts'
import LoadingIcon from '@/icons/LoadingIcon.vue'

interface Errors {
  username?: string[]
  role?: string[]
  redeem_code?: string[]
  password?: string[]
  phone?: string[]
  form?: string[]
}

const router = useRouter()
const message = ref('')
const messageType = ref('success')
const errors = ref<Errors | null>(null)

const { data: user } = useProfile()

const form = reactive({
  username: user.value?.username ?? '',
  role: user.value?.role ?? 'team',
  redeem_code: '',
  password: '',
  full_name: user.value?.full_name ?? '',
  phone: user.value?.phone ?? '',
  city: user.value?.city ?? '',
})

const restrictedRoles = ['jury', 'organizer', 'admin']
const isRestrictedRole = computed(() => restrictedRoles.includes(form.role))

watch(
  () => form.role,
  (newRole) => {
    if (!restrictedRoles.includes(newRole)) {
      form.redeem_code = ''
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

const { mutate: updateProfile, isPending: isUpdatingProfile } = useUpdateProfile()

const handleSubmit = async () => {
  message.value = ''

  const passwordError = getPasswordError(form.password)
  if (passwordError) {
    errors.value = { password: [passwordError] }
    messageType.value = 'error'
    message.value = 'Please fix form errors and try again.'
    return
  }

  updateProfile(
    { body: form },
    {
      onSuccess: () => {
        localStorage.removeItem('needs_onboarding')
        messageType.value = 'success'
        message.value = 'Profile completed successfully.'
        router.push('/')
      },
      onError: (err) => {
        errors.value = err.response?.data as Errors
        messageType.value = 'error'
        message.value = err.response
          ? 'Please fix form errors and try again.'
          : 'Server connection error.'
      },
    },
  )
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

.form-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
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
