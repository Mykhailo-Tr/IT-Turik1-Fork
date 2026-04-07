<template>
  <section class="page-shell teams-page">
    <ui-card>
      <template #header>
        <p class="section-eyebrow">Teams</p>
        <h1 class="section-title">Team directory</h1>
        <p class="section-subtitle">
          Open a team workspace to view details, edit info, and manage members.
        </p>
      </template>

      <template #footer>
        <div class="hero-actions">
          <ui-button asLink to="/teams/create" class="manage-link">Create new team</ui-button>
          <ui-skeleton-loader :loading="isLoadingTeams">
            <template #skeleton>
              <ui-skeleton variant="rect" width="108px" height="30px" />
            </template>

            <span class="meta-pill">Total teams: {{ teams?.length }}</span>
          </ui-skeleton-loader>
        </div>
      </template>
    </ui-card>

    <team-invatations />

    <team-my-teams :teams="teams ?? []" />

    <teams-other-teams :teams="teams ?? []" />
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import { watch } from 'vue'
import TeamInvatations from '../components/teamsView/TeamInvatations.vue'
import TeamMyTeams from '../components/teamsView/TeamMyTeams.vue'
import TeamsOtherTeams from '../components/teamsView/TeamsOtherTeams.vue'
import { useTeams } from '@/queries/teams'
import UiSkeletonLoader from '@/components/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/UiSkeleton.vue'

const { showNotification } = useGlobalNotification()

const { data: teams, isLoading: isLoadingTeams, error: teamsError } = useTeams()

watch(teamsError, (err) => {
  if (err) {
    showNotification(
      err.response ? 'Unable to load teams.' : 'Unable to connect to server.',
      'error',
    )
  }
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
