<template>
  <div class="top-actions" v-if="user?.role === 'admin'">
    <AddEventModal :tournament-id="props.tournamentId" />
  </div>

  <section class="page-shell">
    <ui-skeleton-loader :loading="isEventsLoading">
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
              </div>
            </div>
          </ui-card>
        </div>
      </template>

      <ui-card v-if="isEventsError">
        <div style="display: flex; height: 500px; justify-content: center; align-items: center">
          <p>Error while fetching tournament schedule</p>
        </div>
      </ui-card>

      <div v-else class="events-list">
        <ui-card v-for="event in events" :key="event.title" class="event-card">
          <div class="event-content">
            <div class="event-left-side">
              <div class="event-icon">
                <FinishIcon width="25px" height="25px" />
              </div>

              <p>{{ event.title }}</p>
            </div>

            <div class="event-right-side">
              <p class="text-muted">
                {{ formatDate(event.startAt, { showHours: true }) }}
              </p>
            </div>
          </div>

          <div class="event-actions" v-if="user?.role === 'admin'">
            <EditEventModal
              :event-id="event.id"
              :title="event.title"
              :start-date="event.startAt!"
            />
            <DeleteEventModal :event-id="event.id" :title="event.title" />
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
import FinishIcon from '@/icons/FinishIcon.vue'
import { formatDate } from '@/lib/date'
import { useQuery } from '@tanstack/vue-query'
import EditEventModal from './modals/EditEventModal.vue'
import { useProfile } from '@/queries/accounts'
import DeleteEventModal from './modals/DeleteEventModal.vue'
import AddEventModal from './modals/AddEventModal.vue'

interface Event {
  id: number
  title: string
  startAt: Date
}

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()
const { data: user } = useProfile()

const fetchEvents = async (_tournamentId: number): Promise<Event[]> => {
  await new Promise((resolve) => setTimeout(resolve, 200))

  return [
    {
      id: 1,
      title: 'Opening Ceremony',
      startAt: new Date('2026-04-18T10:00:00'),
    },
    {
      id: 2,
      title: 'Final Event',
      startAt: new Date('2026-04-21T15:00:00'),
    },
  ]
}

const {
  data: events,
  isLoading: isEventsLoading,
  isError: isEventsError,
} = useQuery({
  queryKey: ['events', props.tournamentId],
  queryFn: () => fetchEvents(props.tournamentId),
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

.event-left-side,
.event-right-side {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.top-actions,
.event-actions {
  display: flex;
  gap: 0.6rem;
  justify-content: end;
}

.event-actions {
  padding-top: 14px;
  border-top: 1px solid var(--border);
}
</style>
