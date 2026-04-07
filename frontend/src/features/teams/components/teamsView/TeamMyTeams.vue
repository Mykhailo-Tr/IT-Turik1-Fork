<template>
  <ui-card>
    <header class="section-head">
      <h2>My teams</h2>
      <span class="text-muted">{{ myTeams.length }} joined</span>
    </header>

    <p v-if="myTeams.length === 0" class="text-muted">You are not a member of any team yet.</p>
    <div v-else class="team-grid">
      <ui-card v-for="team in myTeamsPageItems" :key="`my-${team.id}`" class="team-item">
        <div class="team-meta">
          <h3>{{ team.name }}</h3>
          <ui-badge v-if="isCaptain(team)" variant="blue">Captain</ui-badge>
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
        <ui-button asLink variant="outline" size="sm" :to="`/teams/${team.id}`"
          >Open workspace</ui-button
        >
      </ui-card>
    </div>

    <div v-if="myPages > 1" class="pagination">
      <ui-button size="sm" variant="outline" :disabled="myPage === 1" @click="myPage -= 1">
        Prev
      </ui-button>
      <span>Page {{ myPage }} / {{ myPages }}</span>
      <ui-button size="sm" variant="outline" :disabled="myPage === myPages" @click="myPage += 1">
        Next
      </ui-button>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/UiBadge.vue'
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import { useAuth } from '@/composables/useAuth'
import type { GetTeamsResponse } from '@/services/teams/types'
import { computed, ref } from 'vue'

const TEAMS_PER_PAGE = 8

interface Props {
  teams: GetTeamsResponse[]
}

const props = defineProps<Props>()
const auth = useAuth()

const myPage = ref(1)
const myPages = computed(() => Math.max(1, Math.ceil(myTeams.value.length / TEAMS_PER_PAGE)))

const isCaptain = (team: GetTeamsResponse) => team.captain_id === auth.user.value?.id
const captainName = (team: GetTeamsResponse) => {
  const captain = team.members.find((member) => member.id === team.captain_id)
  return captain?.username || `User #${team.captain_id}`
}
const isAcceptedMember = (team: GetTeamsResponse) => team.is_member || isCaptain(team)

const myTeams = computed(() => props.teams.filter((team) => isAcceptedMember(team)))
const myTeamsPageItems = computed(() => {
  const from = (myPage.value - 1) * TEAMS_PER_PAGE
  return myTeams.value.slice(from, from + TEAMS_PER_PAGE)
})
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

@media (max-width: 640px) {
  .section-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
