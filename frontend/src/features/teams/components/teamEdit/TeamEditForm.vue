<template>
  <ui-card class="panel form-panel">
    <header class="panel-head">
      <h2>Team profile settings</h2>
      <span v-if="isCaptain" class="status-badge">Captain access</span>
    </header>

    <p v-if="!isCaptain" class="notice error lock-note">Only team captain can edit this team.</p>

    <form class="form-grid" @submit.prevent="saveTeam">
      <label class="form-label">
        Team name
        <ui-input v-model="form.name" required :disabled="!isCaptain || isSavingChanges" />
      </label>

      <label class="form-label">
        Team email
        <ui-input
          v-model="form.email"
          type="email"
          required
          :disabled="!isCaptain || isSavingChanges"
        />
      </label>

      <label class="form-label">
        Organization
        <ui-input v-model="form.organization" :disabled="!isCaptain || isSavingChanges" />
      </label>

      <label class="form-label">
        Telegram
        <ui-input
          v-model="form.contact_telegram"
          pattern="^@?[A-Za-z][A-Za-z0-9_]{4,31}$"
          title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
          :disabled="!isCaptain || isSavingChanges"
        />
      </label>

      <label class="form-label">
        Discord
        <ui-input
          v-model="form.contact_discord"
          pattern="^@?(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?$"
          title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
          :disabled="!isCaptain || isSavingChanges"
        />
      </label>

      <div class="form-actions full-width">
        <ui-button type="submit" :disabled="!isCaptain || isSavingChanges">
          <loading-icon v-if="isSavingChanges" />
          Save changes
        </ui-button>
        <ui-button asLink variant="outline" :to="`/teams/${team.id}`">Cancel</ui-button>
      </div>
    </form>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiInput from '@/components/UiInput.vue'
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import $api from '@/services'
import { isApiError } from '@/services/apiClient'
import type { GetTeamInfoResponse } from '@/services/teams/types'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

interface Props {
  isCaptain: boolean
  team: GetTeamInfoResponse
}

const props = defineProps<Props>()
const router = useRouter()
const { hideNotification, showNotification } = useGlobalNotification()

const form = ref({
  name: props.team.name,
  email: props.team.email,
  organization: props.team.organization,
  contact_telegram: props.team.contact_telegram,
  contact_discord: props.team.contact_discord,
})

const isSavingChanges = ref(false)

const saveTeam = async () => {
  isSavingChanges.value = true
  hideNotification()

  try {
    await $api.teams.updateInfo(props.team.id, form.value)

    router.push(`/teams/${props.team.id}`)
  } catch (err) {
    if (isApiError(err)) {
      showNotification(
        err.response ? 'Unable to update team.' : 'Server connection error.',
        'error',
      )
    }
  } finally {
    isSavingChanges.value = false
  }
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

.status-badge {
  border-radius: 999px;
  border: 1px solid rgba(20, 184, 166, 0.45);
  background: rgba(20, 184, 166, 0.15);
  color: var(--brand-700);
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
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
