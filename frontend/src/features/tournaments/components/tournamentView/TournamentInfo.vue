<template>
  <ui-card class="tournament-card" :is-error="isError">
    <template #header>
      <h2 class="tournament-title">Tournament Info</h2>
    </template>

    <template #error>
      <div style="display: flex; height: 300px; justify-content: center; align-items: center">
        <p>Error while fetching tournament info (code: {{ error?.code }})</p>
      </div>
    </template>

    <div>
      <p class="text-muted">Name</p>
      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <div style="display: flex; flex-direction: column; gap: 0.3rem">
            <ui-skeleton variant="rect" width="100%" />
            <ui-skeleton variant="rect" width="80%" />
          </div>
        </template>

        <p :title="tournament?.name">{{ truncateText(tournament?.name ?? '', 200) }}</p>
      </ui-skeleton-loader>
    </div>

    <div class="tournament-start">
      <div>
        <p class="text-muted">Start date</p>
        <div class="">
          <ui-skeleton-loader :loading="isLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="180px" />
            </template>

            <p>
              {{
                tournament?.start_date
                  ? formatDate(tournament.start_date, { showHours: true })
                  : '-'
              }}
            </p>
          </ui-skeleton-loader>
        </div>
      </div>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <ui-skeleton variant="rect" width="100px" />
        </template>

        <ui-badge :variant="statusBadgeVariant">{{ tournament?.status }}</ui-badge>
      </ui-skeleton-loader>
    </div>

    <div>
      <p class="text-muted">Description</p>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <div style="display: flex; flex-direction: column; gap: 0.4rem">
            <ui-skeleton variant="rect" width="90%" />
            <ui-skeleton variant="rect" width="70%" />
            <ui-skeleton variant="rect" width="80%" />
          </div>
        </template>

        <p
          :title="tournament?.description"
          @click="toggleDescriptionModal"
          :class="['tournament-description', { large: isDescriptionLarge }]"
        >
          {{ truncateText(tournament?.description ?? '', 190) }}

          <full-screen-icon
            v-if="isDescriptionLarge"
            class="text-muted"
            width="15px"
            height="15px"
            style="display: inline; margin-left: 4px"
          />
        </p>

        <description-modal
          v-model="isDesciptionOpen"
          :description="tournament?.description ?? ''"
        />
      </ui-skeleton-loader>
    </div>

    <div class="tournament-action">
      <!-- TODO add link to round info -->
      <ui-button v-if="currentRound" variant="ghost" class="tournament-action-btn">
        Current round: {{ currentRound.name }}
      </ui-button>

      <join-tournament-btn :tournament-id="props.tournamentId" />
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import { parseApiError } from '@/api'
import UiBadge from '@/components/UiBadge.vue'
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiSkeleton from '@/components/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/UiSkeletonLoader.vue'
import { computed, ref } from 'vue'
import DescriptionModal from './modals/DescriptionModal.vue'
import { truncateText } from '@/lib/utils'
import { formatDate } from '@/lib/date'
import FullScreenIcon from '@/icons/FullScreenIcon.vue'
import { useCurrentRound, useTournamentInfo } from '@/queries/tournaments'
import JoinTournamentBtn from './JoinTournamentBtn.vue'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()
const isDesciptionOpen = ref(false)

const {
  data: tournament,
  isLoading,
  error: tournamentInfoError,
  isError,
} = useTournamentInfo({ id: props.tournamentId })
const error = computed(() => parseApiError(tournamentInfoError.value))
const { data: currentRound } = useCurrentRound({ id: props.tournamentId })

const isDescriptionLarge = computed(() => (tournament.value?.description.length ?? 0) > 190)
const statusBadgeVariant = computed(() => {
  if (tournament.value?.status === 'draft') return 'gray'
  if (tournament.value?.status === 'finished') return 'gray'
  if (tournament.value?.status === 'running') return 'green'
  if (tournament.value?.status === 'registration') return 'orange'

  return 'gray'
})

const toggleDescriptionModal = () => {
  if (!isDescriptionLarge.value) return
  isDesciptionOpen.value = !isDesciptionOpen.value
}
</script>

<style scoped>
.tournament-card {
  flex: 1;
}

.tournament-title {
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.tournament-description {
  border-radius: 6px;
  transition: baclground 2s ease-in;
}

.tournament-description.large:hover {
  cursor: pointer;
  background: color-mix(in srgb, var(--foreground) 8%, transparent);
}

.tournament-start {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tournament-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.7rem;
}

.tournament-action {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tournament-action-btn {
  width: 100%;
}
</style>
