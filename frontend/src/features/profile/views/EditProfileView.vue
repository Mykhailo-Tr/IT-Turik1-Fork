<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div class="head">
          <div>
            <p class="section-eyebrow">User Center</p>
            <h1 class="section-title profile-title">Edit Profile</h1>
          </div>
        </div>

        <p class="section-subtitle">Update your account details below and save your changes.</p>
      </template>

      <form @submit.prevent="handleSubmit" class="profile-form">
        <div class="form-grid">
          <div class="form-item">
            <label class="form-label"> Full name </label>

            <ui-skeleton-loader :loading="isLoading" style="width: 100%">
              <template #skeleton>
                <ui-skeleton variant="rect" height="45px" width="100%" />
              </template>

              <ui-input
                v-model="form.full_name"
                :class="{ 'field-invalid': getFieldError('full_name') }"
                style="width: 100%"
                type="text"
                placeholder="John Doe"
                required
                @blur="touchField('full_name')"
              />
            </ui-skeleton-loader>
            <small v-if="getFieldError('full_name')" class="text-error">{{
              getFieldError('full_name')
            }}</small>
          </div>

          <div class="form-item">
            <label class="form-label"> Username </label>

            <ui-skeleton-loader :loading="isLoading" style="width: 100%">
              <template #skeleton>
                <ui-skeleton variant="rect" height="45px" width="100%" />
              </template>

              <ui-input
                v-model="form.username"
                :class="{ 'field-invalid': getFieldError('username') }"
                style="width: 100%"
                placeholder="johndoe"
                required
                @blur="touchField('username')"
              />
            </ui-skeleton-loader>

            <small v-if="getFieldError('username')" class="text-error">{{
              getFieldError('username')
            }}</small>
          </div>

          <div class="form-item">
            <label class="form-label"> Phone number </label>

            <ui-skeleton-loader :loading="isLoading" style="width: 100%">
              <template #skeleton>
                <ui-skeleton variant="rect" height="45px" width="100%" />
              </template>

              <PhoneField
                v-model="form.phone"
                :error="getFieldError('phone')"
                @update:modelValue="touchField('phone')"
              />
            </ui-skeleton-loader>
          </div>

          <div class="form-item">
            <label class="form-label"> City </label>
            <ui-skeleton-loader :loading="isLoading" style="width: 100%">
              <template #skeleton>
                <ui-skeleton variant="rect" height="45px" width="100%" />
              </template>

              <ui-input
                v-model="form.city"
                :class="{ 'field-invalid': getFieldError('city') }"
                style="width: 100%"
                type="text"
                placeholder="Kyiv"
                required
                @blur="touchField('city')"
              />
            </ui-skeleton-loader>

            <small v-if="getFieldError('city')" class="text-error">{{
              getFieldError('city')
            }}</small>
          </div>
        </div>

        <div class="actions">
          <ui-button type="submit" :disabled="isUpdatingProfile">
            <LoadingIcon v-if="isUpdatingProfile" />
            Save changes
          </ui-button>
          <ui-button variant="outline" @click="isPasswordModalOpen = true"
            >Change Password</ui-button
          >
          <ui-button variant="outline" :disabled="isUpdatingProfile" @click="goBackToProfile"
            >Cancel</ui-button
          >
        </div>
      </form>
    </ui-card>

    <ui-modal v-model="isPasswordModalOpen" @close="resetPasswordState">
      <template #title>
        <h3>Change Password</h3>
      </template>

      <div class="mode-switch">
        <ui-button
          variant="outline-accent"
          class="switch-btn"
          :class="{ active: passwordMode === 'manual' }"
          :disabled="isChangingPassword"
          @click="setPasswordMode('manual')"
        >
          Use Current Password
        </ui-button>
        <ui-button
          variant="outline-accent"
          class="switch-btn"
          :class="{ active: passwordMode === 'recovery' }"
          :disabled="isChangingPassword"
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
        <ui-button type="submit" :disabled="isChangingPassword">
          <loading-icon v-if="isChangingPassword" />
          Update password
        </ui-button>
      </form>

      <form v-else class="password-form" @submit.prevent="handleRecoveryRequest">
        <p class="text-muted">No worries. We will send a secure reset link to your email.</p>
        <div class="form-item">
          <label class="form-label"> Account email </label>
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
        </div>

        <ui-button type="submit" :disabled="isRecoveringPassword">
          <LoadingIcon v-if="isRecoveringPassword" />
          Send reset link
        </ui-button>
      </form>
    </ui-modal>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import PhoneField from '@/features/shared/components/forms/PhoneField.vue'
import UiPasswordField from '@/components/UiPasswordField.vue'
import { useNotification } from '@/features/shared/composables/useNotification'
import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiCard from '@/components/UiCard.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import {
  useChangePassword,
  useForgotPassword,
  useProfile,
  useUpdateProfile,
} from '@/queries/accounts'
import UiModal from '@/components/UiModal.vue'
import UiSkeletonLoader from '@/components/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/UiSkeleton.vue'

interface PasswordErrors {
  current_password?: string[]
  email?: string[]
  new_password?: string[]
  confirm_password?: string[]
  non_field_errors?: string[]
}

type ProfileErrors = Record<FormField, string[]>

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

const { data: user, isLoading } = useProfile()

const form = computed<ProfileForm>(() => ({
  username: user.value?.username ?? '',
  full_name: user.value?.full_name ?? '',
  phone: user.value?.phone ?? '',
  city: user.value?.city ?? '',
}))

const updateProfileErrors = ref<ProfileErrors[] | null>(null)
const touched = ref<TouchedFields>({ full_name: false, username: false, phone: false, city: false })
const isPasswordModalOpen = ref(false)
const passwordMode = ref<PasswordMode>('manual')
const recoveryEmail = computed(() => user.value?.email ?? '')
const passwordErrors = ref<PasswordErrors | null>(null)
const passwordMessage = ref('')
const passwordMessageType = ref<'success' | 'error'>('success')
const passwordForm = ref<PasswordForm>({
  current_password: '',
  new_password: '',
  confirm_password: '',
})
const router = useRouter()
const { showNotification, hideNotification } = useNotification()

const validateFullName = (value: string): string => {
  if (!value?.trim()) return 'Full name is required.'
  if (value.trim().length < 2) return 'Full name must be at least 2 characters.'
  return ''
}

const validateUsername = (value: string): string => {
  if (!value?.trim()) return 'Username is required.'
  if (value.trim().length <= 3) return 'Username must be at least 3 characters.'
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
  if (updateProfileErrors.value?.[field]?.[0]) {
    return updateProfileErrors.value[field]![0]
  }
  if (!touched.value[field]) {
    return ''
  }
  return clientErrors.value[field] || ''
}

const hasClientErrors = (): boolean => Object.values(clientErrors.value).some(Boolean)

const resetPasswordState = () => {
  passwordErrors.value = {}
  passwordMessage.value = ''
  passwordForm.value = {
    current_password: '',
    new_password: '',
    confirm_password: '',
  }
}

const setPasswordMode = (mode: PasswordMode) => {
  passwordMode.value = mode
  passwordErrors.value = {}
  passwordMessage.value = ''
}

const { mutate: updateProfile, isPending: isUpdatingProfile } = useUpdateProfile()

const handleSubmit = () => {
  updateProfileErrors.value = null
  touchAllFields()
  hideNotification()

  if (hasClientErrors()) {
    showNotification('Please fix highlighted fields before saving.', 'error')
    return
  }

  updateProfile(
    { body: form.value },
    {
      onSuccess: () => {
        showNotification('Profile updated successfully.', 'success')
        router.push('/profile')
      },
      onError: (err) => {
        if (err.response) {
          updateProfileErrors.value = err.response.data as ProfileErrors[]
          showNotification('Validation error. Please check your data.', 'error')
        } else {
          showNotification('Server connection error.', 'error')
        }
      },
    },
  )
}

const { mutate: changePassword, isPending: isChangingPassword } = useChangePassword()
const { mutate: forgotPassword, isPending: isRecoveringPassword } = useForgotPassword()

const handlePasswordChange = () => {
  passwordErrors.value = {}
  passwordMessage.value = ''

  changePassword(
    { body: passwordForm.value },
    {
      onSuccess: () => {
        resetPasswordState()
        passwordMessageType.value = 'success'
        passwordMessage.value = 'Password changed successfully.'
        showNotification('Password updated successfully.', 'success')
      },
      onError: (err) => {
        passwordMessageType.value = 'error'
        if (err.response) {
          passwordErrors.value = err.response.data as PasswordErrors
          passwordMessage.value = 'Please fix password form errors.'
        } else {
          passwordMessage.value = 'Server connection error.'
        }
      },
    },
  )
}

const handleRecoveryRequest = () => {
  passwordErrors.value = {}
  passwordMessage.value = ''

  forgotPassword(
    { body: { email: recoveryEmail.value } },
    {
      onSuccess: (data) => {
        passwordMessageType.value = 'success'
        passwordMessage.value = data?.message || 'Password reset email sent successfully.'
        showNotification('Reset link sent. Check your email.', 'success')
      },
      onError: (err) => {
        passwordMessageType.value = 'error'
        if (err.response) {
          passwordErrors.value = err.response.data as PasswordErrors
          passwordMessage.value = 'Could not send reset email.'
        } else {
          passwordMessage.value = 'Server connection error.'
        }
      },
    },
  )
}

const goBackToProfile = () => {
  router.push('/profile')
}
</script>

<style scoped>
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

.form-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
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
  margin-bottom: 0.8rem;
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
