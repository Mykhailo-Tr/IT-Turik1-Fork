<template>
  <ui-card class="tournament-card">
    <template #header>
      <h2 class="tournament-card-title">Teams Info</h2>
    </template>

    <div>
      <ui-input
        v-model="search"
        placeholder="Search team"
        class="team-search"
        :disabled="isTeamsLoading"
      />

      <div class="team-label">
        <p>Team</p>

        <ui-skeleton-loader :loading="isTeamsLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="60px" />
          </template>

          <p class="text-muted">
            {{ filteredTeams.length }} team{{ filteredTeams.length === 1 ? '' : 's' }}
          </p>
        </ui-skeleton-loader>
      </div>

      <div class="teams-list">
        <ui-skeleton-loader :loading="isTeamsLoading">
          <template #skeleton>
            <div style="display: flex; flex-direction: column; gap: 0.4rem">
              <ui-skeleton variant="rect" height="48px" width="100%" />
              <ui-skeleton variant="rect" height="48px" width="100%" />
              <ui-skeleton variant="rect" height="48px" width="100%" />
            </div>
          </template>

          <template v-if="filteredTeams.length">
            <RouterLink
              :to="`/teams/${team.id}`"
              v-for="team in filteredTeams"
              :key="team.id"
              class="team-item"
            >
              <div class="team-info">
                <TeamIcon />
                {{ team.name }}
              </div>

              <ui-badge variant="green"> {{ team.members }} members </ui-badge>
            </RouterLink>
          </template>

          <p v-else class="text-muted">No teams found.</p>
        </ui-skeleton-loader>
      </div>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiBadge from '@/components/UiBadge.vue'
import UiCard from '@/components/UiCard.vue'
import UiInput from '@/components/UiInput.vue'
import UiSkeleton from '@/components/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/UiSkeletonLoader.vue'
import TeamIcon from '@/icons/TeamIcon.vue'
import { useQuery } from '@tanstack/vue-query'
import { RouterLink } from 'vue-router'

interface Team {
  id: number
  name: string
  members: number
}

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()

const search = ref('')

const fetchTeams = async (): Promise<Team[]> => {
  await new Promise((resolve) => setTimeout(resolve, 500))

  return [
    { id: 1, name: 'Alpha Team', members: 32 },
    { id: 2, name: 'Bravo Squad', members: 18 },
    { id: 3, name: 'Phoenix Unit', members: 24 },
    { id: 4, name: 'Storm Crew', members: 12 },
  ]
}

const { data: teams, isLoading: isTeamsLoading } = useQuery({
  queryKey: ['tournament-teams', props.tournamentId],
  queryFn: fetchTeams,
})

const filteredTeams = computed(() => {
  if (!teams.value) return []

  const term = search.value.trim().toLowerCase()

  if (!term) return teams.value

  return teams.value.filter((team) => team.name.toLowerCase().includes(term))
})
</script>

<style scoped>
.tournament-card {
  flex: 1;
}

.tournament-card-title {
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.team-search {
  width: 100%;
  margin-bottom: 1rem;
}

.team-info {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.team-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  padding: 0.7rem 0;
}

.team-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.teams-list {
  overflow-y: auto;
  max-height: 215px;
}
</style>
