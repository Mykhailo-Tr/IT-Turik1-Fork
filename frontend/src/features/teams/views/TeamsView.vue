<template>
  <section class="page-shell teams-page">
    <ui-card>
      <p class="section-eyebrow">Teams</p>
      <h1 class="section-title">Team directory</h1>
      <p class="section-subtitle">
        Open a team workspace to view details, edit info, and manage members.
      </p>
      <div class="hero-actions">
        <ui-button asLink to="/teams/create" class="manage-link">Create new team</ui-button>
        <span class="meta-pill">Total teams: {{ teams?.length }}</span>
      </div>
    </ui-card>

    <ui-card v-if="loading">Loading teams...</ui-card>

    <template v-else>
      <team-invatations @respondedToInvatation="fetchTeams()" />

      <!-- TODO: add vue query, so i can fetch once and cache using key -->
      <!-- Then invalidate key or refetch when making changes -->
      <team-my-teams :teams="teams ?? []" />

      <teams-other-teams :teams="teams ?? []" @sendedJoinRequest="fetchTeams()" />
    </template>
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import $api from '@/services'
import { isApiError } from '@/services/apiClient'
import { onMounted, ref } from 'vue'
import TeamInvatations from '../components/teamsView/TeamInvatations.vue'
import TeamMyTeams from '../components/teamsView/TeamMyTeams.vue'
import type { GetTeamsResponse } from '@/services/teams/types'
import TeamsOtherTeams from '../components/teamsView/TeamsOtherTeams.vue'

const { showNotification } = useGlobalNotification()

const teams = ref<GetTeamsResponse[] | null>(null)
const loading = ref(false)

const fetchTeams = async () => {
  loading.value = true

  try {
    const response = await $api.teams.getTeams()

    teams.value = response.data
  } catch (err) {
    if (isApiError(err)) {
      showNotification(
        err.response ? 'Unable to load teams.' : 'Unable to connect to server.',
        'error',
      )
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTeams()
})
</script>

<style scoped>
.teams-page {
  gap: 1.2rem;
}

.hero-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  align-items: center;
}

.manage-link {
  display: inline-flex;
  text-decoration: none;
}

.meta-pill {
  border: 1px solid rgba(15, 23, 42, 0.12);
  border-radius: 999px;
  padding: 0.33rem 0.7rem;
  font-size: 0.84rem;
  color: var(--ink-700);
  background: rgba(255, 255, 255, 0.8);
}
</style>
