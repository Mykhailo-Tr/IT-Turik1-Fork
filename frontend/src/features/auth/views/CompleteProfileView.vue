<template>
  <section class="page-shell centered">
    <ui-card class="complete-card">
      <p class="section-eyebrow">Final Step</p>
      <h1 class="section-title">Complete your profile</h1>
      <p class="section-subtitle">
        Choose your role and review your account details before continuing.
      </p>

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
          </div>
        </div>

        <div class="form-item">
          <label class="form-label full-width"> Full name </label>
          <ui-input v-model="form.full_name" />
          <small v-if="errors?.full_name" class="text-error">{{ errors.full_name[0] }}</small>
        </div>

        <div class="form-item">
          <label class="form-label"> Phone </label>
          <PhoneField v-model="form.phone" placeholder="Enter phone number" />
          <small v-if="errors?.phone" class="text-error">{{ errors.phone[0] }}</small>
        </div>

        <div class="form-item">
          <label class="form-label"> City </label>
          <ui-input v-model="form.city" />
          <small v-if="errors?.city" class="text-error">{{ errors.city[0] }}</small>
        </div>

        <ui-button class="submit-btn" :disabled="isUpdatingProfile" type="submit">
          Complete registration
          <loading-icon v-if="isUpdatingProfile" />
        </ui-button>
      </form>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import PhoneField from '@/components/shared/PhoneField.vue'
import UiPasswordField from '@/components/UiPasswordField.vue'
import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiSelect from '@/components/UiSelect.vue'
import UiCard from '@/components/UiCard.vue'
import { useProfile, useUpdateProfile } from '@/queries/accounts'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useNotification } from '@/composables/useNotification'
import type { UserRole } from '@/api/dbTypes'

interface Form {
  username: string
  role: UserRole
  redeem_code: string
  password: string
  full_name: string
  phone: string
  city: string
}

const router = useRouter()
const { showNotification } = useNotification()
const { data: user } = useProfile()

type Errors = Partial<Record<keyof Form, string[]>>
const errors = ref<Partial<Errors>>({})
const resetErrors = () => {
  errors.value = {}
}

const form = reactive<Form>({
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
  resetErrors()

  const passwordError = getPasswordError(form.password)
  if (passwordError) {
    errors.value = { password: [passwordError] }
    return
  }

  updateProfile(
    { body: form },
    {
      onSuccess: () => {
        localStorage.removeItem('needs_onboarding')
        router.push('/')
      },
      onError: (err) => {
        if (err.response) {
          Object.entries(err.response.data.details).forEach(([key, messages]) => {
            errors.value[key as keyof Errors] = messages
          })
        } else {
          showNotification('Network error. Try again later', 'error')
        }
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
