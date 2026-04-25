<template>
  <ui-button v-bind="$attrs" variant="secondary" @click="isOpen = true">Forgot Password</ui-button>

  <ui-modal v-model="isOpen">
    <template #title>
      <h2>Forgot password</h2>
    </template>

    <form class="password-form" @submit.prevent="handleRecoveryRequest">
      <p class="text-muted">No worries. We will send a secure reset link to your email.</p>
      <div class="form-item">
        <label class="form-label"> Account email </label>
        <ui-input
          v-model="recoveryEmail"
          :is-invalid="!!error?.details.email"
          type="email"
          autocomplete="email"
          required
        />
        <small v-if="error?.details.email" class="text-error">{{ error?.details.email[0] }}</small>
      </div>

      <ui-button type="submit" :disabled="isRecoveringPassword">
        <LoadingIcon v-if="isRecoveringPassword" />
        Send reset link
      </ui-button>
    </form>
  </ui-modal>
</template>

<script setup lang="ts">
import { parseError } from '@/api'
import UiInput from '@/components/UiInput.vue'
import UiModal from '@/components/UiModal.vue'
import UiButton from '@/components/UiButton.vue'
import { useNotification } from '@/composables/useNotification'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useForgotPassword, useProfile } from '@/queries/accounts'
import { computed, ref } from 'vue'

const { showNotification } = useNotification()
const { data: user } = useProfile()

const isOpen = ref(false)
const recoveryEmail = computed(() => user.value?.email ?? '')

const {
  mutate: forgotPassword,
  isPending: isRecoveringPassword,
  error: forgotPasswordError,
} = useForgotPassword()
const error = computed(() => parseError(forgotPasswordError.value))

const handleRecoveryRequest = () => {
  forgotPassword(
    { body: { email: recoveryEmail.value } },
    {
      onSuccess: () => {
        showNotification('Reset was sent. Check your email.', 'success')
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
</style>
