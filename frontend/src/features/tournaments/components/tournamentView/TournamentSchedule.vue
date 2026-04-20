<template>
  <section class="page-shell">
    <ui-skeleton-loader :loading="isLoading">
      <template #skeleton>
        <div class="events-list">
          <ui-card v-for="i in 5" :key="i">
            <div class="event-content">
              <div class="event-left-side">
                <ui-skeleton variant="rounded" width="50px" height="50px" />

                <ui-skeleton variant="rect" width="100px" />
              </div>
              <div class="event-dates">
                <ui-skeleton variant="rect" width="150px" />
                <ui-skeleton variant="rect" width="150px" />
              </div>
            </div>
          </ui-card>
        </div>
      </template>

      <ui-card v-if="isRoundsError || isEventsError">
        <div style="display: flex; height: 500px; justify-content: center; align-items: center">
          <p>Error while fetching tournament schedule</p>
        </div>
      </ui-card>

      <div v-else class="events-list">
        <ui-card v-for="event in schedule" :key="event.title" class="event-card">
          <div class="event-content">
            <div class="event-left-side">
              <div class="event-icon">
                <CameraIcon v-if="event.type === 'event'" width="25px" height="25px" />
                <FinishIcon v-else width="25px" height="25px" />
              </div>

              <p>{{ event.title }}</p>
            </div>

            <div :class="['event-dates', { range: !!event.startDate && !!event.endDate }]">
              <p v-if="event.startDate" class="text-muted start-date">
                {{ formatDate(event.startDate, { showHours: true }) }}
              </p>
              <p class="text-muted">{{ formatDate(event.endDate, { showHours: true }) }}</p>
            </div>
          </div>
        </ui-card>
      </div>
    </ui-skeleton-loader>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/UiCard.vue'
import UiSkeleton from '@/components/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/UiSkeletonLoader.vue'
import CameraIcon from '@/icons/CameraIcon.vue'
import FinishIcon from '@/icons/FinishIcon.vue'
import { formatDate } from '@/lib/utils'
import { useQuery } from '@tanstack/vue-query'
import { computed } from 'vue'

interface Round {
  title: string
  endAt: Date
}

interface Event {
  title: string
  startAt: Date
  endAt: Date
}

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const fetchRounds = async (_tournamentId: number): Promise<Round[]> => {
  await new Promise((resolve) => setTimeout(resolve, 500))

  return [
    {
      title: 'Round 2',
      endAt: new Date('2026-04-20T18:00:00'),
    },
    {
      title: 'Round 1',
      endAt: new Date('2026-04-19T12:00:00'),
    },
  ]
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const fetchEvents = async (_tournamentId: number): Promise<Event[]> => {
  await new Promise((resolve) => setTimeout(resolve, 200))

  return [
    {
      title: 'Opening Ceremony',
      startAt: new Date('2026-04-18T10:00:00'),
      endAt: new Date('2026-08-18T10:00:00'),
    },
    {
      title: 'Final Event',
      startAt: new Date('2026-04-21T15:00:00'),
      endAt: new Date('2026-10-12T10:00:00'),
    },
  ]
}

const {
  data: rounds,
  isLoading: roundsLoading,
  isError: isRoundsError,
} = useQuery({
  queryKey: ['rounds', props.tournamentId],
  queryFn: () => fetchRounds(props.tournamentId),
})

const {
  data: events,
  isLoading: eventsLoading,
  isError: isEventsError,
} = useQuery({
  queryKey: ['events', props.tournamentId],
  queryFn: () => fetchEvents(props.tournamentId),
})

const isLoading = computed(() => roundsLoading.value || eventsLoading.value)

const schedule = computed(() => {
  const roundItems =
    rounds.value?.map((round) => ({
      type: 'round' as const,
      title: round.title,
      startDate: null,
      endDate: round.endAt,
      sortDate: round.endAt,
    })) ?? []

  const eventItems =
    events.value?.map((event) => ({
      type: 'event' as const,
      title: event.title,
      startDate: event.startAt,
      endDate: event.endAt,
      sortDate: event.startAt,
    })) ?? []

  return [...roundItems, ...eventItems].sort((a, b) => a.sortDate.getTime() - b.sortDate.getTime())
})
</script>

<style scoped>
.event-card {
  position: relative;
}

.event-card::before {
  content: '';
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  left: -30px;
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background: var(--primary);
}

.event-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  padding-left: 20px;
  margin-left: 10px;
  border-left: 1px solid var(--border);
}

.event-icon {
  width: 50px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--primary);
  color: #fff;
  border-radius: 50%;
}

.event-left-side {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.event-dates {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.event-dates.range {
  padding-left: 15px;
  border-left: 2px solid var(--border);
  border-radius: 5px 0 0 5px;
}
</style>
