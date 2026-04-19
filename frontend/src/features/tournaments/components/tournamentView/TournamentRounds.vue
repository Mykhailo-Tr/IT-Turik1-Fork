<template>
  <div class="actions" v-if="user?.role === 'admin'">
    <ui-button asLink :to="`/tournaments/${props.tournamentId}/rounds/create`"
      >Create round</ui-button
    >
  </div>
  <section>
    <ui-skeleton-loader :loading="isLoading">
      <template #skeleton>
        <div class="rounds-list">
          <ui-card v-for="i in 3" :key="i" class="round-card">
            <template #header>
              <div class="round-header">
                <ui-skeleton variant="rect" width="180px" height="24px" />
                <ui-skeleton variant="rect" width="80px" height="24px" />
              </div>
            </template>

            <div style="display: flex; flex-direction: column; gap: 0.3rem">
              <ui-skeleton variant="rect" width="220px" />
              <ui-skeleton variant="rect" width="220px" />
            </div>

            <div class="round-actions">
              <ui-skeleton variant="rect" width="110px" height="36px" />
            </div>
          </ui-card>
        </div>
      </template>

      <ui-card v-if="isError">
        <div style="display: flex; height: 300px; justify-content: center; align-items: center">
          <p>Error while fetching rounds (code: {{ error?.code }})</p>
        </div>
      </ui-card>

      <div v-else class="rounds-list">
        <ui-card v-for="round in rounds" :key="round.id" class="round-card">
          <template #header>
            <div class="round-header">
              <h4>{{ truncateText(round.title, 70) }}</h4>
              <ui-badge :variant="badgeVariant(round.status)">{{
                badgeLabel(round.status)
              }}</ui-badge>
            </div>
          </template>

          <div class="round-dates">
            <p class="text-muted">Start: {{ formatDate(round.startAt, { showHours: true }) }}</p>
            <p class="text-muted">End: {{ formatDate(round.endAt, { showHours: true }) }}</p>
          </div>

          <div class="round-actions">
            <ui-button size="sm" variant="secondary" @click="openDetails(round)">
              View details
            </ui-button>
          </div>
        </ui-card>
      </div>
    </ui-skeleton-loader>

    <ui-modal v-model="isDetailsOpen" maxWidth="1100px" @close="closeDetails">
      <template #title>
        <h2>{{ selectedRound?.title ?? 'Round details' }}</h2>
      </template>

      <div class="details-grid">
        <ui-card>
          <template #header>
            <h3>Technical requirements</h3>
          </template>

          <editor-content class="details-editor" :editor="requirementsEditor" />
        </ui-card>

        <ui-card>
          <template #header>
            <h3>Must have</h3>
          </template>

          <editor-content class="details-editor" :editor="mustHaveEditor" />
        </ui-card>
      </div>

      <template #footer>
        <ui-button variant="secondary" @click="closeDetails">Close</ui-button>
      </template>
    </ui-modal>
  </section>
</template>

<script setup lang="ts">
import { parseError } from '@/api'
import UiBadge from '@/components/UiBadge.vue'
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiModal from '@/components/UiModal.vue'
import UiSkeleton from '@/components/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/UiSkeletonLoader.vue'
import { formatDate, truncateText } from '@/lib/utils'
import { useQuery } from '@tanstack/vue-query'
import type { JSONContent } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import { computed, ref, watch } from 'vue'
import type { Variants } from '@/components/UiBadge.vue'
import { useProfile } from '@/queries/accounts'

interface Round {
  id: number
  title: string
  status: 'active' | 'upcoming' | 'completed'
  startAt: Date
  endAt: Date
  technicalRequirements: JSONContent
  mustHave: JSONContent
}

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()

const { data: user } = useProfile()

const mockRequirements: JSONContent = {
  type: 'doc',
  content: [
    {
      type: 'heading',
      attrs: { level: 2 },
      content: [{ type: 'text', text: 'Requirements' }],
    },
    {
      type: 'bulletList',
      content: [
        {
          type: 'listItem',
          content: [
            {
              type: 'paragraph',
              content: [{ type: 'text', text: 'Use TypeScript for the solution.' }],
            },
          ],
        },
        {
          type: 'listItem',
          content: [
            {
              type: 'paragraph',
              content: [{ type: 'text', text: 'Provide short README with run instructions.' }],
            },
          ],
        },
      ],
    },
  ],
}

const mockMustHave: JSONContent = {
  type: 'doc',
  content: [
    {
      type: 'heading',
      attrs: { level: 2 },
      content: [{ type: 'text', text: 'Must have' }],
    },
    {
      type: 'orderedList',
      content: [
        {
          type: 'listItem',
          content: [
            {
              type: 'paragraph',
              content: [{ type: 'text', text: 'Form validation for required fields.' }],
            },
          ],
        },
        {
          type: 'listItem',
          content: [
            {
              type: 'paragraph',
              content: [{ type: 'text', text: 'Responsive UI layout.' }],
            },
          ],
        },
      ],
    },
  ],
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const fetchRounds = async (_tournamentId: number): Promise<Round[]> => {
  await new Promise((resolve) => setTimeout(resolve, 450))

  return [
    {
      id: 2,
      title: 'Round 2',
      status: 'active',
      startAt: new Date('2026-04-20T10:00:00'),
      endAt: new Date('2026-04-23T18:00:00'),
      technicalRequirements: mockRequirements,
      mustHave: mockMustHave,
    },
    {
      id: 1,
      title: 'Round 1',
      status: 'completed',
      startAt: new Date('2026-04-19T10:00:00'),
      endAt: new Date('2026-04-19T18:00:00'),
      technicalRequirements: mockRequirements,
      mustHave: mockMustHave,
    },
    {
      id: 3,
      title: 'Round 3',
      status: 'upcoming',
      startAt: new Date('2026-04-19T10:00:00'),
      endAt: new Date('2026-04-19T18:00:00'),
      technicalRequirements: mockRequirements,
      mustHave: mockMustHave,
    },
  ]
}

const {
  data,
  isLoading,
  error: roundsError,
  isError,
} = useQuery({
  queryKey: ['tournament-rounds', props.tournamentId],
  queryFn: () => fetchRounds(props.tournamentId),
})
const error = computed(() => parseError(roundsError.value))
const rounds = computed(() => data.value ?? [])

const isDetailsOpen = ref(false)
const selectedRound = ref<Round | null>(null)

const requirementsEditor = useEditor({
  extensions: [StarterKit],
  content: '',
  editable: false,
  editorProps: {
    attributes: {
      class: 'prose',
      'aria-readonly': 'true',
    },
  },
})

const mustHaveEditor = useEditor({
  extensions: [StarterKit],
  content: '',
  editable: false,
  editorProps: {
    attributes: {
      class: 'prose',
      'aria-readonly': 'true',
    },
  },
})

watch(
  () => selectedRound.value,
  (round) => {
    requirementsEditor.value?.commands.setContent(round?.technicalRequirements ?? '', {
      emitUpdate: false,
    })
    mustHaveEditor.value?.commands.setContent(round?.mustHave ?? '', { emitUpdate: false })
  },
)

function openDetails(round: Round) {
  selectedRound.value = round
  isDetailsOpen.value = true
}

function closeDetails() {
  isDetailsOpen.value = false
  selectedRound.value = null
}

function badgeLabel(status: Round['status']) {
  if (status === 'active') return 'Active'
  if (status === 'upcoming') return 'Upcoming'
  return 'Completed'
}

function badgeVariant(status: Round['status']): Variants {
  if (status === 'active') return 'green'
  if (status === 'upcoming') return 'orange'
  return 'gray'
}
</script>

<style scoped>
.actions {
  display: flex;
  justify-content: end;
  align-items: center;
}

.rounds-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
}

.round-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
}

.round-actions {
  display: flex;
  justify-content: end;
  align-items: center;
}

.round-dates {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.round-card {
  min-width: 0;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.details-editor {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.75rem;
  background: var(--input);
  height: min(60vh, 520px);
  overflow: auto;
}

.details-editor :deep(.ProseMirror) {
  outline: none;
  min-height: 100%;
}

@media (max-width: 900px) {
  .details-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1024px) {
  .rounds-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .rounds-list {
    grid-template-columns: 1fr;
  }
}
</style>
