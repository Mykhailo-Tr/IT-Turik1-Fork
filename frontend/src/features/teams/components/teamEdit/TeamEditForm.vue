<template>
  <ui-card class="panel form-panel">
    <header class="panel-head">
      <h2>Team profile settings</h2>
      <ui-badge variant="green">Captain access</ui-badge>
    </header>

    <form class="form-grid" @submit.prevent="handleSubmit">
      <label class="form-label">
        Team name
        <ui-skeleton-loader :loading="props.loading" style="width: 100%">
          <template #skeleton>
            <ui-skeleton variant="rect" height="45px" width="100%" />
          </template>

          <ui-input v-model="form.name" required :disabled="isSavingChanges" style="width: 100%" />
        </ui-skeleton-loader>
      </label>

      <label class="form-label">
        Team email
        <ui-skeleton-loader :loading="props.loading" style="width: 100%">
          <template #skeleton>
            <ui-skeleton variant="rect" height="45px" width="100%" />
          </template>

          <ui-input
            v-model="form.email"
            type="email"
            required
            :disabled="isSavingChanges"
            style="width: 100%"
        /></ui-skeleton-loader>
      </label>

      <label class="form-label">
        Organization
        <ui-skeleton-loader :loading="props.loading" style="width: 100%">
          <template #skeleton>
            <ui-skeleton variant="rect" height="45px" width="100%" />
          </template>

          <ui-input v-model="form.organization" :disabled="isSavingChanges" style="width: 100%" />
        </ui-skeleton-loader>
      </label>

      <label class="form-label">
        Telegram
        <ui-skeleton-loader :loading="props.loading" style="width: 100%">
          <template #skeleton>
            <ui-skeleton variant="rect" height="45px" width="100%" />
          </template>

          <ui-input
            v-model="form.contact_telegram"
            pattern="^@?[A-Za-z][A-Za-z0-9_]{4,31}$"
            title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
            :disabled="isSavingChanges"
            style="width: 100%"
          />
        </ui-skeleton-loader>
      </label>

      <label class="form-label">
        Discord
        <ui-skeleton-loader :loading="props.loading" style="width: 100%">
          <template #skeleton>
            <ui-skeleton variant="rect" height="45px" width="100%" />
          </template>

          <ui-input
            v-model="form.contact_discord"
            pattern="^@?(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?$"
            title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
            :disabled="isSavingChanges"
            style="width: 100%"
          />
        </ui-skeleton-loader>
      </label>

      <div class="form-actions full-width">
        <ui-button type="submit" :disabled="isSavingChanges || props.loading || props.isError">
          <loading-icon v-if="isSavingChanges" />
          Save changes
        </ui-button>
        <ui-button asLink variant="secondary" :to="`/teams/${team?.id}`" :disabled="props.loading"
          >Cancel</ui-button
        >
      </div>
    </form>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiInput from '@/components/UiInput.vue'
import { useNotification } from '@/composables/useNotification'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import type { GetTeamInfoResponse } from '@/api/teams/types'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUpdateTeamInfo } from '@/queries/teams'
import UiSkeletonLoader from '@/components/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/UiSkeleton.vue'
import UiBadge from '@/components/UiBadge.vue'

interface Props {
  team?: GetTeamInfoResponse
  loading: boolean
  isError?: boolean
}

const props = defineProps<Props>()
const router = useRouter()
const { hideNotification, showNotification } = useNotification()

const form = ref({
  name: props.team?.name ?? '',
  email: props.team?.email ?? '',
  organization: props.team?.organization ?? '',
  contact_telegram: props.team?.contact_telegram ?? '',
  contact_discord: props.team?.contact_discord ?? '',
})

const isSavingChanges = ref(false)

const { mutate: updateTeam } = useUpdateTeamInfo()

const handleSubmit = () => {
  if (!props.team) return
  hideNotification()

  updateTeam(
    { teamId: props.team.id, body: form.value },
    {
      onSuccess: () => {
        router.push(`/teams/${props.team?.id}`)
      },
      onError: (err) => {
        showNotification(
          err.response ? 'Unable to update team.' : 'Server connection error.',
          'error',
        )
      },
    },
  )
}
</script>

<style scoped>
.panel {
  border: 1px solid var(--line-soft);
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  margin-bottom: 0.9rem;
}

.panel-head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.15rem;
}

.lock-note {
  margin-top: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.full-width {
  grid-column: 1 / -1;
}

.form-actions {
  display: flex;
  gap: 0.6rem;
  align-items: center;
}

@media (max-width: 760px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
