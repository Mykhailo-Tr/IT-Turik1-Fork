<template>
  <ui-card class="tournament-card">
    <template #header>
      <h2 class="tournament-card-title">Tournament Info</h2>
    </template>

    <div>
      <p class="text-muted">Name</p>
      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <ui-skeleton variant="rect" width="100%" />
        </template>

        <p>{{ tournament?.name }}</p>
      </ui-skeleton-loader>
    </div>

    <div class="tournament-start">
      <div>
        <p class="text-muted">Start date</p>
        <div class="">
          <ui-skeleton-loader :loading="isLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" />
            </template>

            <p>
              {{
                tournament?.startAt.toLocaleDateString('uk-UA', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                  hour: 'numeric',
                  minute: 'numeric',
                })
              }}
            </p>
          </ui-skeleton-loader>
        </div>
      </div>

      <ui-badge>Running</ui-badge>
    </div>

    <div>
      <p class="text-muted">Description</p>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <ui-skeleton variant="rect" height="100px" width="100%" />
        </template>

        <p>{{ tournament?.description }}</p>
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
      <ui-button tournament-action-btn>View details</ui-button>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/UiBadge.vue'
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiSkeleton from '@/components/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/UiSkeletonLoader.vue'
import { useQuery } from '@tanstack/vue-query'

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

const fetchItem = async (id: number): Promise<Response> => {
  await new Promise((resolve) => setTimeout(resolve, 500))

  return {
    id: id,
    name: `Item ${id}`,
    description: `Item description ${id}`,
    status: Math.random() > 0.5 ? 'Running' : 'Registration open',
    startAt: new Date(),
  }
}

const { data: tournament, isLoading } = useQuery({
  queryKey: ['tournaments', props.tournamentId],
  queryFn: () => fetchItem(props.tournamentId),
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
