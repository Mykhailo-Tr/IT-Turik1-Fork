<template>
  <section class="page-shell">
    <ui-card class="profile-card">
      <div class="head">
        <div>
          <p class="section-eyebrow">User Center</p>
          <h1 class="section-title profile-title">Edit Profile</h1>
        </div>
      </div>

      <p class="section-subtitle">Update your account details below and save your changes.</p>

      <div v-if="loadingProfile" class="state-box">Loading profile...</div>
      <div v-else-if="profileError" class="state-box error">{{ profileError }}</div>

      <form v-else @submit.prevent="handleUpdate" class="profile-form">
        <div class="form-grid">
          <label class="form-label">
            Full name
            <ui-input
              v-model="form.full_name"
              :class="{ 'field-invalid': getFieldError('full_name') }"
              type="text"
              placeholder="John Doe"
              required
              @blur="touchField('full_name')"
            />
            <small v-if="getFieldError('full_name')" class="text-error">{{
              getFieldError('full_name')
            }}</small>
          </label>

          <label class="form-label">
            Username
            <ui-input
              v-model="form.username"
              :class="{ 'field-invalid': getFieldError('username') }"
              placeholder="johndoe"
              required
              @blur="touchField('username')"
            />
            <small v-if="getFieldError('username')" class="text-error">{{
              getFieldError('username')
            }}</small>
          </label>

          <label class="form-label">
            Phone number
            <PhoneField
              v-model="form.phone"
              :error="getFieldError('phone')"
              @update:modelValue="touchField('phone')"
            />
          </label>

          <label class="form-label">
            City
            <ui-input
              v-model="form.city"
              :class="{ 'field-invalid': getFieldError('city') }"
              type="text"
              placeholder="Kyiv"
              required
              @blur="touchField('city')"
            />
            <small v-if="getFieldError('city')" class="text-error">{{
              getFieldError('city')
            }}</small>
          </label>
        </div>

        <div class="actions">
          <ui-button type="submit" :disabled="loading">
            {{ loading ? 'Saving...' : 'Save changes' }}
          </ui-button>
          <ui-button variant="outline" :disabled="loading" @click="openPasswordModal">
            Change Password
          </ui-button>
          <ui-button variant="outline" :disabled="loading" @click="goBackToProfile">
            Cancel
          </ui-button>
        </div>
      </form>
    </ui-card>

    <div v-if="isPasswordModalOpen" class="modal-backdrop" @click.self="closePasswordModal">
      <article
        class="modal-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="password-modal-title"
      >
        <div class="password-head">
          <h2 id="password-modal-title" class="panel-title">Change Password</h2>
          <button
            class="icon-close"
            type="button"
            :disabled="passwordLoading"
            @click="closePasswordModal"
          >
            ×
          </button>
        </div>

        <div class="mode-switch">
          <ui-button
            variant="outline-accent"
            class="switch-btn"
            :class="{ active: passwordMode === 'manual' }"
            :disabled="passwordLoading"
            @click="setPasswordMode('manual')"
          >
            Use Current Password
          </ui-button>
          <ui-button
            variant="outline-accent"
            class="switch-btn"
            :class="{ active: passwordMode === 'recovery' }"
            :disabled="passwordLoading"
            @click="setPasswordMode('recovery')"
          >
            Forgot Password
          </ui-button>
        </div>

        <p v-if="passwordMessage" :class="['notice', passwordMessageType]">{{ passwordMessage }}</p>

        <form
          v-if="passwordMode === 'manual'"
          class="password-form"
          @submit.prevent="handlePasswordChange"
        >
          <label class="form-label">
            Current password
            <ui-password-field
              v-model="passwordForm.current_password"
              autocomplete="current-password"
              required
            />
            <small v-if="passwordErrors?.current_password" class="text-error">{{
              passwordErrors.current_password[0]
            }}</small>
          </label>

          <label class="form-label">
            New password
            <ui-password-field
              v-model="passwordForm.new_password"
              autocomplete="new-password"
              required
            />
            <small v-if="passwordErrors?.new_password" class="text-error">{{
              passwordErrors.new_password[0]
            }}</small>
          </label>

          <label class="form-label">
            Confirm new password
            <ui-password-field
              v-model="passwordForm.confirm_password"
              autocomplete="new-password"
              required
            />
            <small v-if="passwordErrors?.confirm_password" class="text-error">{{
              passwordErrors.confirm_password[0]
            }}</small>
          </label>

          <small v-if="passwordErrors?.non_field_errors" class="text-error">{{
            passwordErrors.non_field_errors[0]
          }}</small>
          <ui-button type="submit" :disabled="passwordLoading">
            {{ passwordLoading ? 'Updating...' : 'Update password' }}
          </ui-button>
        </form>

        <form v-else class="password-form" @submit.prevent="handleRecoveryRequest">
          <p class="text-muted">No worries. We will send a secure reset link to your email.</p>
          <label class="form-label">
            Account email
            <ui-input
              v-model="recoveryEmail"
              :class="{ 'field-invalid': passwordErrors?.email }"
              type="email"
              autocomplete="email"
              required
            />
            <small v-if="passwordErrors?.email" class="text-error">{{
              passwordErrors.email[0]
            }}</small>
          </label>

          <ui-button type="submit" :disabled="passwordLoading">
            {{ passwordLoading ? 'Sending...' : 'Send reset link' }}
          </ui-button>
        </form>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PhoneField from '@/features/shared/components/forms/PhoneField.vue'
import UiPasswordField from '@/components/UiPasswordField.vue'
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import $api from '@/services'
import { isApiError } from '@/services/apiClient'
import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiCard from '@/components/UiCard.vue'

interface PasswordErrors {
  current_password?: string[]
  email?: string[]
  new_password?: string[]
  confirm_password?: string[]
  non_field_errors?: string[]
}

type PasswordMode = 'recovery' | 'manual'

type TouchField = 'full_name' | 'phone' | 'city' | 'username'

type FormField = TouchField

interface ProfileForm {
  username: string
  full_name: string
  phone: string
  city: string
}

interface TouchedFields {
  full_name: boolean
  username: boolean
  phone: boolean
  city: boolean
}

interface PasswordForm {
  current_password: string
  new_password: string
  confirm_password: string
}

const form = ref<ProfileForm>({ username: '', full_name: '', phone: '', city: '' })
const loading = ref(false)
const loadingProfile = ref(true)
const profileError = ref('')
const errors = ref<Record<FormField, string[]> | null>(null)
const touched = ref<TouchedFields>({ full_name: false, username: false, phone: false, city: false })
const isPasswordModalOpen = ref(false)
const passwordMode = ref<PasswordMode>('manual')
const recoveryEmail = ref('')
const passwordLoading = ref(false)
const passwordErrors = ref<PasswordErrors | null>(null)
const passwordMessage = ref('')
const passwordMessageType = ref<'success' | 'error'>('success')
const passwordForm = ref<PasswordForm>({
  current_password: '',
  new_password: '',
  confirm_password: '',
})
const router = useRouter()
const { showNotification } = useGlobalNotification()

const validateFullName = (value: string): string => {
  if (!value?.trim()) return 'Full name is required.'
  if (value.trim().length < 2) return 'Full name must be at least 2 characters.'
  return ''
}

const validateUsername = (value: string): string => {
  if (!value?.trim()) return 'Username is required.'
  if (value.trim().length < 3) return 'Username must be at least 3 characters.'
  if (!/^[A-Za-z0-9@.+_-]+$/.test(value)) {
    return 'Use letters, numbers, and @ . + - _ only.'
  }
  return ''
}

const validatePhone = (value: string): string => {
  if (!value?.trim()) return 'Phone number is required.'
  if (!/^\+?1?\d{9,15}$/.test(value)) return 'Use 9-15 digits with an optional + prefix.'
  return ''
}

const validateCity = (value: string): string => {
  if (!value?.trim()) return 'City is required.'
  if (value.trim().length < 2) return 'City must be at least 2 characters.'
  return ''
}

const clientErrors = computed(() => ({
  full_name: validateFullName(form.value.full_name),
  username: validateUsername(form.value.username),
  phone: validatePhone(form.value.phone),
  city: validateCity(form.value.city),
}))

const touchField = (field: TouchField): void => {
  touched.value[field] = true
}

const touchAllFields = (): void => {
  touched.value = { full_name: true, username: true, phone: true, city: true }
}

const getFieldError = (field: FormField): string => {
  if (errors.value?.[field]?.[0]) {
    return errors.value[field]![0]
  }
  if (!touched.value[field]) {
    return ''
  }
  return clientErrors.value[field] || ''
}

const hasClientErrors = (): boolean => Object.values(clientErrors.value).some(Boolean)

// TODO: Remove
// const logoutToLogin = () => {
//   localStorage.removeItem('access')
//   localStorage.removeItem('refresh')
//   localStorage.removeItem('needs_onboarding')
//   router.push('/login')
// }

const fetchProfile = async () => {
  loadingProfile.value = true
  profileError.value = ''

  const token = localStorage.getItem('access')
  if (!token) return router.push('/login')

  try {
    const response = await $api.accounts.getProfile(token)

    if (response.data.needs_onboarding) {
      localStorage.setItem('needs_onboarding', '1')
      router.push('/complete-profile')
      return
    }

    form.value = {
      username: response.data.username || '',
      full_name: response.data.full_name || '',
      phone: response.data.phone || '',
      city: response.data.city || '',
    }
    recoveryEmail.value = response.data.email || ''
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        if (err.response.status === 401) return router.push('/login')

        profileError.value = 'Could not load profile information.'
      } else {
      }
      profileError.value = 'Server connection error.'
    }
  } finally {
    loadingProfile.value = false
  }
}

const resetPasswordState = () => {
  passwordErrors.value = {}
  passwordMessage.value = ''
  passwordForm.value = {
    current_password: '',
    new_password: '',
    confirm_password: '',
  }
}

const openPasswordModal = () => {
  isPasswordModalOpen.value = true
}

const closePasswordModal = () => {
  if (passwordLoading.value) return
  isPasswordModalOpen.value = false
  passwordMode.value = 'manual'
  resetPasswordState()
}

const setPasswordMode = (mode: PasswordMode) => {
  passwordMode.value = mode
  passwordErrors.value = {}
  passwordMessage.value = ''
}

const handleUpdate = async () => {
  loading.value = true
  errors.value = null
  touchAllFields()

  if (hasClientErrors()) {
    showNotification('Please fix highlighted fields before saving.', 'error')
    loading.value = false
    return
  }

  const token = localStorage.getItem('access')
  if (!token) return router.push('/login')

  try {
    await $api.accounts.updateProfile(token, form.value)

    showNotification('Profile updated successfully.', 'success')
    setTimeout(() => {
      router.push('/profile')
    }, 550)
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        if (err.response.status === 401) router.push('/login')

        errors.value = err.response.data
        showNotification('Validation error. Please check your data.', 'error')
      } else {
        showNotification('Server connection error.', 'error')
      }
    }
  } finally {
    loading.value = false
  }
}

const handlePasswordChange = async () => {
  passwordLoading.value = true
  passwordErrors.value = {}
  passwordMessage.value = ''

  const token = localStorage.getItem('access')
  if (!token) return router.push('/login')

  try {
    const response = await $api.accounts.changePassword(token, passwordForm.value)

    resetPasswordState()
    passwordMessageType.value = 'success'
    passwordMessage.value = response.data.message || 'Password changed successfully.'
    showNotification('Password updated successfully.', 'success')
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        passwordErrors.value = err.response.data
        passwordMessageType.value = 'error'
        passwordMessage.value = err.response.data.detail || 'Please fix password form errors.'
      } else {
        passwordMessageType.value = 'error'
        passwordMessage.value = 'Server connection error.'
      }
    }
  } finally {
    passwordLoading.value = false
  }
}

const handleRecoveryRequest = async () => {
  passwordLoading.value = true
  passwordErrors.value = {}
  passwordMessage.value = ''

  try {
    const response = await $api.accounts.resetPassword({
      type: 'forgot',
      email: recoveryEmail.value,
    })

    passwordMessageType.value = 'success'
    passwordMessage.value = response?.data.message || 'Password reset email sent successfully.'
    showNotification('Reset link sent. Check your email.', 'success')
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        passwordErrors.value = err.response.data
        passwordMessageType.value = 'error'
        passwordMessage.value = err.response.data.detail || 'Could not send reset email.'
      } else {
        passwordMessageType.value = 'error'
        passwordMessage.value = 'Server connection error.'
      }
    }
  } finally {
    passwordLoading.value = false
  }
}

const goBackToProfile = () => {
  router.push('/profile')
}

onMounted(fetchProfile)
</script>

<style scoped>
.profile-card {
  width: min(100%, 860px);
  margin: 0 auto;
  padding: 1.7rem;
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

.profile-title {
  margin-top: 0.2rem;
}

.section-subtitle {
  margin-bottom: 0;
}

.state-box {
  margin-top: 1rem;
  border-radius: 14px;
  border: 1px solid var(--line-soft);
  padding: 0.9rem 1rem;
  background: rgba(255, 255, 255, 0.85);
}

.state-box.error {
  color: #991b1b;
  border-color: rgba(220, 38, 38, 0.25);
  background: rgba(254, 242, 242, 0.9);
}

.form-grid {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.field-invalid {
  border-color: rgba(220, 38, 38, 0.7);
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.12);
}

.accent-hover:hover {
  border-color: var(--brand-500);
  color: var(--brand-700);
  background: rgba(20, 184, 166, 0.08);
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: grid;
  place-items: center;
  z-index: 70;
  padding: 1rem;
}

.modal-card {
  width: min(100%, 580px);
  border-radius: 18px;
  border: 1px solid var(--line-soft);
  background: #fff;
  box-shadow: var(--shadow-lg);
  padding: 1.1rem;
  display: grid;
  gap: 0.9rem;
}

.password-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.panel-title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.2rem;
}

.icon-close {
  border: 1px solid var(--line-strong);
  background: #fff;
  color: var(--ink-700);
  width: 2.1rem;
  height: 2.1rem;
  border-radius: 10px;
  font-size: 1.2rem;
  cursor: pointer;
}

.icon-close:hover {
  background: rgba(15, 23, 42, 0.06);
}

.mode-switch {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.switch-btn {
  padding: 0.55rem 0.8rem;
}

.switch-btn.active {
  border-color: var(--brand-500);
  color: var(--brand-700);
  background: rgba(20, 184, 166, 0.12);
}

.password-form {
  display: grid;
  gap: 0.75rem;
}

@media (max-width: 760px) {
  .profile-card {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .actions {
    flex-direction: column;
  }

  .mode-switch {
    width: 100%;
  }
}
</style>
<style scoped src="../../teams/styles/status-tags.css"></style>
