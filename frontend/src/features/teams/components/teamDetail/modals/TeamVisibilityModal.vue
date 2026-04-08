<template>
  <ui-button
    size="sm"
    variant="warning"
    :disabled="visibilityLoading"
    @click="toggleVisibilityModal"
  >
    Change visibility
  </ui-button>

  <ui-modal
    v-model="isVisibilityModalOpen"
    title="Change team visibility"
    :close-on-backdrop="!visibilityLoading"
    :show-close="!visibilityLoading"
  >
    <p class="modal-text">
      Select the new visibility for <ui-badge variant="green">{{ team?.name }}</ui-badge
      ><br />
      This affects who can discover and join your team.
    </p>

    <div class="visibility-options">
      <label class="visibility-option" :class="{ selected: selectedVisibility === true }">
        <ui-input
          type="radio"
          name="visibility"
          :value="true"
          :checked="selectedVisibility === true"
          :disabled="visibilityLoading"
          @change="selectedVisibility = true"
        />
        <div class="visibility-option-content">
          <div class="visibility-option-header">
            <eye-in-circle />
            <strong>Public</strong>
          </div>
          <p>Anyone can find and request to join this team.</p>
        </div>
      </label>

      <label class="visibility-option" :class="{ selected: selectedVisibility === false }">
        <ui-input
          type="radio"
          name="visibility"
          :value="false"
          :checked="selectedVisibility === false"
          :disabled="visibilityLoading"
          @change="selectedVisibility = false"
        />
        <div class="visibility-option-content">
          <div class="visibility-option-header">
            <lock-icon />
            <strong>Private</strong>
          </div>
          <p>Only invited members can find and access this team.</p>
        </div>
      </label>
    </div>

    <div v-if="selectedVisibility !== team?.is_public" class="visibility-confirm-note">
      <danger-icon />
      <span>
        You are about to change this team from
        <strong>{{ team?.is_public ? 'Public' : 'Private' }}</strong>
        to
        <strong>{{ selectedVisibility ? 'Public' : 'Private' }}</strong
        >.
      </span>
    </div>

    <p v-if="visibilityError" class="text-error modal-error">{{ visibilityError }}</p>

    <template #footer>
      <ui-button
        size="sm"
        variant="outline"
        type="button"
        :disabled="visibilityLoading"
        @click="toggleVisibilityModal"
      >
        Cancel
      </ui-button>
      <ui-button
        variant="warning"
        size="sm"
        type="button"
        :disabled="visibilityLoading || selectedVisibility === team?.is_public"
        @click="confirmChangeVisibility"
      >
        <loading-icon v-if="visibilityLoading" size="sm" />
        {{ visibilityLoading ? 'Saving...' : 'Confirm change' }}
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import UiBadge from '@/components/UiBadge.vue'
import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiModal from '@/components/UiModal.vue'
import { useNotification } from '@/features/shared/composables/useNotification'
import DangerIcon from '@/icons/DangerIcon.vue'
import EyeInCircle from '@/icons/EyeInCircle.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import LockIcon from '@/icons/LockIcon.vue'
import type { GetTeamInfoResponse } from '@/api/teams/types'
import { ref } from 'vue'
import { useChangeTeamVisibility } from '@/queries/teams'

interface Props {
  team?: GetTeamInfoResponse
}

const emit = defineEmits<{
  (e: 'changedTeamVisibility', newTeamValue: GetTeamInfoResponse): void
}>()

const props = defineProps<Props>()
const { showNotification, hideNotification } = useNotification()

const selectedVisibility = ref(props.team?.is_public)
const visibilityLoading = ref(false)
const visibilityError = ref<string | null>(null)
const isVisibilityModalOpen = ref(false)

const toggleVisibilityModal = () => {
  isVisibilityModalOpen.value = !isVisibilityModalOpen.value
}

const { mutate: changeTeamVisibility } = useChangeTeamVisibility()

const confirmChangeVisibility = async () => {
  if (!props.team || !selectedVisibility.value) return

  visibilityLoading.value = true
  hideNotification()

  changeTeamVisibility(
    { teamId: props.team.id, body: { is_public: selectedVisibility.value } },
    {
      onSuccess: (data) => {
        showNotification(
          `Team visibility changed to ${props.team?.is_public ? 'Public' : 'Private'}.`,
          'success',
        )
        emit('changedTeamVisibility', data)

        toggleVisibilityModal()
      },
      onError: (err) => {
        showNotification(
          err.response ? 'Unable to change team visibility.' : 'Unable to change team visibility.',
          'error',
        )
      },
    },
  )
}
</script>

<style scoped>
.visibility-options {
  display: grid;
  gap: 0.6rem;
  margin: 1rem 0 0.8rem;
}

.visibility-option {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 0.9rem;
  border: 1.5px solid var(--line-soft);
  border-radius: 10px;
  cursor: pointer;
  transition:
    border-color 0.15s,
    background 0.15s;
}

.visibility-option:hover {
  border-color: var(--brand-500, #14b8a6);
  background: rgba(20, 184, 166, 0.04);
}

.visibility-option.selected {
  border-color: var(--brand-500, #14b8a6);
  background: rgba(20, 184, 166, 0.06);
}

.visibility-option-content {
  flex: 1;
}

.visibility-option-content p {
  margin: 0.2rem 0 0;
  font-size: 0.84rem;
  color: var(--ink-600);
}

.visibility-option-header {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.visibility-option-icon {
  width: 1rem;
  height: 1rem;
  color: var(--ink-600);
}

.danger-zone-icon {
  width: 0.95rem;
  height: 0.95rem;
  flex-shrink: 0;
}

.visibility-confirm-note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.8rem;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 8px;
  font-size: 0.87rem;
  color: #78350f;
  margin-bottom: 0.5rem;
}
</style>
