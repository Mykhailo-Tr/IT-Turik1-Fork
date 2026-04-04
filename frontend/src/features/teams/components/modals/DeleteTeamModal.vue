<template>
  <ui-button size="sm" variant="danger" @click="isDeleteModalOpen = true">Delete team</ui-button>

  <ui-modal v-model="isDeleteModalOpen" title="Delete team" :close-on-backdrop="!deleteTeamLoading">
    <p class="modal-text">
      This action cannot be undone. Enter
      <ui-badge :value="props.team.name" variant="red" />
      to confirm.
    </p>

    <ui-input
      v-model="deleteConfirmInput"
      :placeholder="props.team.name"
      :disabled="deleteTeamLoading"
    />

    <p v-if="deleteError" class="text-error">{{ deleteError }}</p>

    <template #footer>
      <ui-button
        variant="outline"
        size="sm"
        :disabled="deleteTeamLoading"
        @click="closeDeleteModal"
      >
        Cancel
      </ui-button>

      <ui-button variant="danger" size="sm" :disabled="!canDeleteTeam" @click="deleteTeam">
        {{ deleteTeamLoading ? 'Deleting...' : 'Delete permanently' }}
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import UiBadge from '@/components/UiBadge.vue'
import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiModal from '@/components/UiModal.vue'
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import $api from '@/services'
import { isApiError } from '@/services/apiClient'
import type { GetTeamInfoResponse } from '@/services/teams/types'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

interface Props {
  team: GetTeamInfoResponse
}

const props = defineProps<Props>()
const router = useRouter()
const { hideNotification } = useGlobalNotification()

const emit = defineEmits<{
  (e: 'deleted'): void
}>()

const isDeleteModalOpen = ref(false)
const deleteConfirmInput = ref('')
const deleteTeamLoading = ref(false)
const deleteError = ref('')

const canDeleteTeam = computed(
  () => deleteConfirmInput.value === props.team.name && !deleteTeamLoading.value,
)

function closeDeleteModal() {
  isDeleteModalOpen.value = false
}

const deleteTeam = async () => {
  if (!canDeleteTeam.value) {
    deleteError.value = `Please enter "${props.team.name}" exactly.`
    return
  }

  deleteTeamLoading.value = true
  deleteError.value = ''
  hideNotification()

  try {
    await $api.teams.deleteTeam(props.team.id)

    closeDeleteModal()
    emit('deleted')
  } catch (err) {
    if (isApiError(err)) {
      if (err.response?.status === 401) return router.push('/login')
      deleteError.value = err.response ? 'Unable to delete team.' : 'Server connection error.'
    }
  } finally {
    deleteTeamLoading.value = false
  }
}
</script>
