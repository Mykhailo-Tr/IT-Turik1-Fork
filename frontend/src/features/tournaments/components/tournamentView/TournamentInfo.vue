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
              {{ tournament?.startAt ? formatDate(tournament?.startAt) : '-' }}
            </p>
          </ui-skeleton-loader>
        </div>
      </div>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <ui-skeleton variant="rect" width="100px" />
        </template>

        <ui-badge>Running</ui-badge>
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
          class="tournament-description"
        >
          {{ truncateText(tournament?.description ?? '', 190) }}

          <full-screen-icon
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
      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <ui-button variant="ghost" class="tournament-action-btn">
            <ui-skeleton variant="rect" width="100%" />
          </ui-button>
        </template>

        <ui-button variant="ghost" class="tournament-action-btn">
          Current round: Round 2 (Active)
        </ui-button>
      </ui-skeleton-loader>
      <ui-button :disabled="isLoading">Join tournament</ui-button>
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
import { useQuery } from '@tanstack/vue-query'
import { computed, ref } from 'vue'
import DescriptionModal from './modals/DescriptionModal.vue'
import { truncateText } from '@/lib/utils'
import { formatDate } from '@/lib/date'
import FullScreenIcon from '@/icons/FullScreenIcon.vue'

interface Response {
  id: number
  name: string
  description: string
  status: string
  startAt: Date
}

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()
const isDesciptionOpen = ref(false)

const toggleDescriptionModal = () => {
  isDesciptionOpen.value = !isDesciptionOpen.value
}

const fetchItem = async (id: number): Promise<Response> => {
  await new Promise((resolve) => setTimeout(resolve, 500))

  return {
    id: id,
    name: `Item ${id}`,
    description: `"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."`,
    status: Math.random() > 0.5 ? 'Running' : 'Registration open',
    startAt: new Date(),
  }
}

const {
  data: tournament,
  isLoading,
  error: tournamentInfoError,
  isError,
} = useQuery({
  queryKey: ['tournaments', props.tournamentId],
  queryFn: () => fetchItem(props.tournamentId),
})
const error = computed(() => parseApiError(tournamentInfoError.value))
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

.tournament-description:hover {
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
