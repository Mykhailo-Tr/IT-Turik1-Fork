<template>
  <ui-card class="panel info-panel">
    <header class="panel-head">
      <h2>Team profile</h2>
      <ui-badge v-if="props.isCaptain" variant="green">You are team captain</ui-badge>
    </header>

    <div class="info-grid">
      <div class="info-item">
        <span>Name</span>
        <strong>{{ props.team.name }}</strong>
      </div>
      <div class="info-item">
        <span>Email</span>
        <strong>{{ props.team.email }}</strong>
      </div>
      <div class="info-item">
        <span>Organization</span>
        <strong>{{ props.team.organization || '-' }}</strong>
      </div>
      <div class="info-item">
        <span>Captain</span>
        <strong>{{ captainName }}</strong>
      </div>
      <div class="info-item">
        <span>Members count</span>
        <strong>{{ props.team.members.length }}</strong>
      </div>
      <div class="info-item">
        <span>Visibility</span>
        <strong>{{ props.team.is_public ? 'Public' : 'Private' }}</strong>
      </div>
    </div>

    <div v-if="!props.isCaptain" class="status-line">
      <p v-if="props.team.my_invitation_status" class="text-muted">
        Your invitation status: {{ props.team.my_invitation_status }}
      </p>
      <p v-if="props.team.my_join_request_status" class="text-muted">
        Your join request status: {{ props.team.my_join_request_status }}
      </p>
    </div>

    <div class="info-actions">
      <ui-button
        v-if="props.team.can_request_to_join"
        size="sm"
        :disabled="joinRequestLoading"
        @click="sendJoinRequest"
      >
        <loading-icon v-if="joinRequestLoading" size="md" />
        {{ joinRequestLoading ? 'Sending...' : 'Request to join this team' }}
      </ui-button>

      <ui-button v-if="canLeaveTeam" variant="danger" size="sm" @click="leaveTeam">
        Leave team
      </ui-button>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/UiBadge.vue'
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import $api from '@/services'
import { isApiError } from '@/services/apiClient'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { GetTeamInfoResponse } from '@/services/teams/types'

interface Props {
  team: GetTeamInfoResponse
  isCaptain: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  /** Captain confirmed delete */
  (e: 'deleted'): void
  /** Member wants to leave */
  (e: 'leave'): void
}>()

const router = useRouter()
const { showNotification, hideNotification } = useGlobalNotification()

const captainName = computed(() => {
  const captain = props.team.members.find((member) => member.id === props.team.captain_id)
  return captain?.username || `User #${props.team.captain_id}`
})

// ── Join Request ────────────────────────────────────────────────────
const joinRequestLoading = ref(false)

const sendJoinRequest = async () => {
  joinRequestLoading.value = true
  hideNotification()
  try {
    await $api.teams.sendJoinRequest(props.team.id)

    emit('deleted')
    showNotification('Join request sent.', 'success')
  } catch (err) {
    if (isApiError(err)) {
      if (err.response?.status === 401) return router.push('/login')
      showNotification(
        err.response ? 'Unable to send join request.' : 'Server connection error.',
        'error',
      )
    }
  } finally {
    joinRequestLoading.value = false
  }
}

// ── Leave Team ────────────────────────────────────────────────────
const canLeaveTeam = computed(() => props.team.is_member && !props.isCaptain)

const leaveTeam = async () => {
  try {
    await $api.teams.leave(props.team.id)
    emit('leave')
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        showNotification('Unable to leave team.', 'error')
      } else {
        showNotification('Unable to connect to server.', 'error')
      }
    }
  }
}
</script>

<style scoped>
.panel {
  padding: 1.2rem;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  margin-bottom: 0.9rem;
}

.info-grid {
  display: grid;
  gap: 0.65rem;
}

.info-item {
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  padding: 0.7rem;
  background: rgba(255, 255, 255, 0.9);
}

.info-item span {
  display: block;
  color: var(--ink-500);
  font-size: 0.8rem;
}

.info-item strong {
  color: var(--ink-900);
}

.info-actions {
  margin-top: 0.75rem;
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
}

.status-line {
  margin-top: 0.75rem;
}

.status-line p {
  margin: 0.35rem 0 0;
}

.modal-text {
  margin: 0 0 0.75rem;
  font-size: 0.9rem;
  color: var(--ink-700);
  line-height: 1.55;
}

.modal-text code {
  background: #f1f5f9;
  border: 1px solid var(--line-soft);
  border-radius: 6px;
  padding: 0.1rem 0.35rem;
  font-family: 'SF Mono', ui-monospace, monospace;
  font-size: 0.85em;
}

.modal-error {
  margin: 0.5rem 0 0;
  font-size: 0.8rem;
}
</style>
