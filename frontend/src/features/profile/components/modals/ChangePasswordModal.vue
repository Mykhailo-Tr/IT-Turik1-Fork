<template>
  <ui-button v-bind="$attrs" variant="secondary" @click="isOpen = true">Change Password</ui-button>

  <ui-modal v-model="isOpen" @close="resetPasswordState">
    <template #title>
      <h2>Change password</h2>
    </template>

    <form class="password-form" @submit.prevent="handlePasswordChange">
      <div class="form-item">
        <label class="form-label"> Current password </label>
        <ui-password-field
          v-model="passwordForm.current_password"
          :is-invalid="!!error?.details.current_password"
          autocomplete="current-password"
          required
        />
        <small v-if="error?.details.current_password" class="text-error">{{
          error?.details.current_password[0]
        }}</small>
      </div>

      <div class="form-item">
        <label class="form-label"> New password </label>
        <ui-password-field
          v-model="passwordForm.new_password"
          :is-invalid="!!error?.details.new_password"
          autocomplete="new-password"
          required
        />
        <small v-if="error?.details.new_password" class="text-error">{{
          error?.details.new_password[0]
        }}</small>
      </div>

      <div class="form-item">
        <label class="form-label"> Confirm new password </label>
        <ui-password-field
          v-model="passwordForm.confirm_password"
          :is-invalid="!!error?.details.confirm_password"
          autocomplete="new-password"
          required
        />
        <small v-if="error?.details.confirm_password" class="text-error">{{
          error?.details.confirm_password[0]
        }}</small>
      </div>

      <p class="auth-link" style="text-align: end">
        <router-link to="/forgot-password">Forgot password?</router-link>
      </p>

      <ui-button type="submit" :disabled="isChangingPassword">
        <LoadingIcon v-if="isChangingPassword" />
        Update password
      </ui-button>
    </form>
  </ui-modal>
</template>

<script setup lang="ts">
import { parseError } from '@/api'
import UiButton from '@/components/UiButton.vue'
import UiModal from '@/components/UiModal.vue'
import UiPasswordField from '@/components/UiPasswordField.vue'
import { useNotification } from '@/composables/useNotification'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useChangePassword } from '@/queries/accounts'
import { computed, ref } from 'vue'

interface PasswordForm {
  current_password: string
  new_password: string
  confirm_password: string
}

const passwordForm = ref<PasswordForm>({
  current_password: '',
  new_password: '',
  confirm_password: '',
})

const isOpen = ref(false)

const { showNotification } = useNotification()
const {
  mutate: changePassword,
  isPending: isChangingPassword,
  error: changePasswordError,
} = useChangePassword()
const error = computed(() => parseError(changePasswordError.value))

const resetPasswordState = () => {
  passwordForm.value = {
    current_password: '',
    new_password: '',
    confirm_password: '',
  }
}

const handlePasswordChange = () => {
  if (passwordForm.value.confirm_password !== passwordForm.value.new_password) {
  }
  changePassword(
    { body: passwordForm.value },
    {
      onSuccess: () => {
        resetPasswordState
        showNotification('Password updated successfully.', 'success')
      },
    },
  )
}
</script>

<style scoped>
.password-form {
  display: grid;
  gap: 0.75rem;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
</style>
