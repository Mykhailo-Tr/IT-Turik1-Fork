<template>
  <section class="page-shell teams-edit-page">
    <ui-card class="hero-card">
      <template #header>
        <p class="section-eyebrow">Team workspace</p>

        <h1 class="section-title">
          Edit
          <ui-skeleton-loader style="display: inline-block" :loading="isLoadingTeamInfo">
            <template #skeleton>
              <ui-skeleton variant="rect" width="150px" />
            </template>

            <span>{{ team?.name || 'team' }}</span>
          </ui-skeleton-loader>
        </h1>
      </template>

      <template #footer>
        <div class="hero-actions">
          <ui-button asLink variant="outline" size="sm" :to="team ? `/teams/${team.id}` : '/teams'"
            >Back to team</ui-button
          >
        </div>
      </template>
    </ui-card>

    <ui-card v-if="teamInfoError" class="state-card text-error">{{ teamInfoError }}</ui-card>

    <div class="workspace-grid">
      <team-edit-form :loading="isLoadingTeamInfo" :team="team" />

      <team-manage-members :loading="isLoadingTeamInfo" :team="team" />
    </div>
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import { computed, watchEffect } from 'vue'
import TeamEditForm from '../components/teamEdit/TeamEditForm.vue'
import { useRoute, useRouter } from 'vue-router'
import TeamManageMembers from '../components/teamEdit/TeamManageMembers.vue'
import { useTeamInfo } from '@/queries/teams'
import { useProfile } from '@/queries/accounts'
import UiSkeletonLoader from '@/components/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/UiSkeleton.vue'

const route = useRoute()
const router = useRouter()

const { data: user } = useProfile()

const teamId = computed(() => Number(route.params.id))
const { data: team, isLoading: isLoadingTeamInfo, error: teamInfoError } = useTeamInfo(teamId.value)

watchEffect(() => {
  if (user.value && team.value) {
    if (team.value.captain_id !== user.value.id) {
      router.push('/')
    }
  }
})
</script>

<style scoped>
.teams-edit-page {
  gap: 1.2rem;
}

.hero-card,
.state-card,
.panel {
  padding: 1.2rem;
}

.hero-card {
  background: linear-gradient(135deg, rgba(13, 148, 136, 0.14), rgba(15, 23, 42, 0.03)), #fff;
  border: 1px solid rgba(13, 148, 136, 0.22);
}

.hero-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  align-items: start;
}
</style>
