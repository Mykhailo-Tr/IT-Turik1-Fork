<template>
  <ui-card>
    <header class="section-head">
      <h2>Other teams</h2>
      <span class="text-muted">{{ otherTeams.length }} available</span>
    </header>

    <p v-if="otherTeams.length === 0" class="text-muted">No other teams available.</p>
    <div v-else class="team-grid">
      <article v-for="team in otherTeamsPageItems" :key="`other-${team.id}`" class="team-item">
        <div class="team-meta">
          <h3>{{ team.name }}</h3>
        </div>
        <p class="text-muted">Visibility: {{ team.is_public ? 'Public' : 'Private' }}</p>
        <p class="text-muted">Captain: {{ captainName(team) }}</p>
        <p class="text-muted">Members: {{ team.members.length }}</p>
        <p v-if="team.my_invitation_status" class="text-muted">
          My invitation: {{ team.my_invitation_status }}
        </p>
        <p v-if="team.my_join_request_status" class="text-muted">
          My join request: {{ team.my_join_request_status }}
        </p>
        <ui-button
          size="sm"
          variant="outline"
          v-if="team.can_request_to_join"
          :disabled="joinRequestLoadingByTeam[team.id]"
          @click="sendJoinRequest(team.id)"
        >
          {{ joinRequestLoadingByTeam[team.id] ? 'Sending...' : 'Request to join' }}
        </ui-button>
        <ui-button asLink variant="outline" size="sm" :to="`/teams/${team.id}`"
          >Open workspace</ui-button
        >
      </article>
    </div>

    <div v-if="otherPages > 1" class="pagination">
      <ui-button
        size="sm"
        variant="outline"
        class="btn-soft"
        :disabled="otherPage === 1"
        @click="otherPage -= 1"
        type="button"
      >
        Prev
      </ui-button>
      <span>Page {{ otherPage }} / {{ otherPages }}</span>
      <ui-button
        size="sm"
        variant="outline"
        :disabled="otherPage === otherPages"
        @click="otherPage += 1"
        type="button"
      >
        Next
      </ui-button>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import { useAuth } from '@/composables/useAuth'
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import $api from '@/services'
import { isApiError } from '@/services/apiClient'
import type { JoinRequestId, TeamId } from '@/services/dbTypes'
import type { GetTeamsResponse } from '@/services/teams/types'
import { computed, ref } from 'vue'

const OTHER_TEAMS_PER_PAGE = 8

interface Props {
  teams: GetTeamsResponse[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'sendedJoinRequest'): void
}>()
const auth = useAuth()
const { hideNotification, showNotification } = useGlobalNotification()

const otherPage = ref(1)
const joinRequestLoadingByTeam = ref<Record<JoinRequestId, boolean>>({})

const isCaptain = (team: GetTeamsResponse) => team.captain_id === auth.user.value?.id
const captainName = (team: GetTeamsResponse) => {
  const captain = team.members.find((member) => member.id === team.captain_id)
  return captain?.username || `User #${team.captain_id}`
}
const isAcceptedMember = (team: GetTeamsResponse) => team.is_member || isCaptain(team)

const otherTeams = computed(() => props.teams.filter((team) => !isAcceptedMember(team)))
const otherPages = computed(() =>
  Math.max(1, Math.ceil(otherTeams.value.length / OTHER_TEAMS_PER_PAGE)),
)
const otherTeamsPageItems = computed(() => {
  const from = (otherPage.value - 1) * OTHER_TEAMS_PER_PAGE
  return otherTeams.value.slice(from, from + OTHER_TEAMS_PER_PAGE)
})

const sendJoinRequest = async (teamId: TeamId) => {
  joinRequestLoadingByTeam.value = {
    ...joinRequestLoadingByTeam.value,
    [teamId]: true,
  }
  hideNotification()

  try {
    await $api.teams.sendJoinRequest(teamId)

    emit('sendedJoinRequest')
    showNotification('Join request sent.', 'success')
  } catch (err) {
    if (isApiError(err)) {
      showNotification(
        err.response ? 'Unable to send join request.' : 'Unable to connect to server.',
        'error',
      )
    }
  }
}
</script>

<style scoped>
.teams-card {
  padding: 1.2rem;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  margin-bottom: 0.8rem;
}

.section-head h2 {
  margin: 0;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.9rem;
}

.team-item {
  border: 1px solid var(--line-soft);
  border-radius: 16px;
  background: #fff;
  padding: 0.95rem;
  display: grid;
  gap: 0.45rem;
}

.team-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.team-meta h3 {
  margin: 0;
  font-family: var(--font-display);
}

.team-item p {
  margin: 0;
}

.pagination {
  margin-top: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.btn-soft {
  border: 1px solid var(--line-strong);
  background: #fff;
  border-radius: 10px;
  padding: 0.4rem 0.65rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.btn-soft:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .section-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
