<template>
  <ui-button
    variant="danger"
    :disabled="auth.isLoading.value || isLoading"
    @click="isDeleteModalOpen = true"
    type="button"
  >
    Delete account
  </ui-button>

  <ui-modal v-model="isDeleteModalOpen" title="Delete account">
    <p class="modal-text">
      This action cannot be undone. Enter
      <ui-badge variant="red">{{ expectedDeleteText }}</ui-badge>
      to confirm.
    </p>

    <ui-input
      v-model="deleteConfirmInput"
      :placeholder="expectedDeleteText"
      :disabled="isLoading"
    />

    <p v-if="deleteError">{{ deleteError }}</p>

    <template #footer>
      <ui-button
        variant="outline"
        size="sm"
        :disabled="isLoading"
        @click="isDeleteModalOpen = false"
      >
        Cancel
      </ui-button>
      <ui-button size="sm" variant="danger" :disabled="!canDelete" @click="handleDeleteAccount">
        <loading-icon v-if="isLoading" />
        Delete permanently
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import UiBadge from '@/components/UiBadge.vue'
import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiModal from '@/components/UiModal.vue'
import { useAuth } from '@/composables/useAuth'
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import $api from '@/services'
import { isApiError } from '@/services/apiClient'
import { computed, ref } from 'vue'

const auth = useAuth()
const { showNotification, hideNotification } = useGlobalNotification()

const isDeleteModalOpen = ref(false)
const deleteError = ref<string | null>(null)
const isLoading = ref(false)
const deleteConfirmInput = ref('')
const expectedDeleteText = computed(() => auth.user.value?.username || '')

const canDelete = computed(
  () =>
    Boolean(expectedDeleteText.value) &&
    deleteConfirmInput.value === expectedDeleteText.value &&
    !isLoading.value,
)

const handleDeleteAccount = async () => {
  if (deleteConfirmInput.value !== expectedDeleteText.value) {
    deleteError.value = `Please enter "${expectedDeleteText.value}" exactly.`
    return
  }

  isLoading.value = true
  deleteError.value = ''
  hideNotification()

  try {
    const response = await $api.accounts.deleteAccount()

    if (response.status === 204 || response.status === 200) {
      auth.logout()
      return
    }
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        showNotification('Unable to delete account.', 'error')
      } else {
        showNotification('Server connection error.', 'error')
      }
    }
  } finally {
    isLoading.value = false
  }
}
</script>
