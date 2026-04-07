<template>
  <section class="page-shell teams-edit-page">
    <ui-card class="hero-card">
      <p class="section-eyebrow">Team workspace</p>
      <h1 class="section-title">Edit {{ team?.name || 'team' }}</h1>
      <div class="hero-actions">
        <ui-button asLink variant="outline" size="sm" :to="team ? `/teams/${team.id}` : '/teams'"
          >Back to team</ui-button
        >
      </div>
    </ui-card>

    <!-- TODO replace this skeletons with skeleton ones -->
    <ui-card v-if="loading" class="state-card text-muted">Loading team editor...</ui-card>
    <ui-card v-else-if="loadError" class="state-card text-error">{{ loadError }}</ui-card>

    <template v-else-if="team">
      <div class="workspace-grid">
        <team-edit-form :team="team" :isCaptain="isCaptain" />

        <team-manage-members
          :team="team"
          :isCaptain="isCaptain"
          :users="users"
          @memberDeleted="refetchStates()"
          @invitedMember="refetchStates()"
        />
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import { computed, onMounted, ref } from 'vue'
import TeamEditForm from '../components/teamEdit/TeamEditForm.vue'
import type { GetTeamInfoResponse } from '@/services/teams/types'
import { isApiError } from '@/services/apiClient'
import { useRoute } from 'vue-router'
import $api from '@/services'
import { useAuth } from '@/composables/useAuth'
import TeamManageMembers, { type Member } from '../components/teamEdit/TeamManageMembers.vue'
import { useGlobalNotification } from '@/features/shared/lib/notifications'

const route = useRoute()
const auth = useAuth()
const { showNotification } = useGlobalNotification()

const team = ref<GetTeamInfoResponse | null>(null)
const users = ref<Member[]>([])
const teamId = computed(() => Number(route.params.id))

const loading = ref(false)
const loadError = ref<string | null>(null)

const isCaptain = computed(() => team.value?.captain_id === auth.user.value?.id)

const refetchStates = async () => {
  await Promise.all([fetchTeamInfo(), fetchUsers()])
}

const fetchTeamInfo = async () => {
  if (!teamId.value) {
    loadError.value = 'Invalid team id.'
    return false
  }

  loading.value = true

  try {
    const response = await $api.teams.getTeamInfo(teamId.value)

    team.value = response.data
    return true
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        if (err.response.status === 404) {
          loadError.value = 'Team not found.'
          team.value = null
          return
        }

        loadError.value = 'Unable to load team information.'
      } else {
        loadError.value = 'Unable to connect to server.'
      }
    }
  } finally {
    loading.value = false
  }
}

const fetchUsers = async () => {
  try {
    const response = await $api.accounts.getUsers()

    users.value = response.data
    return true
  } catch (err) {
    if (isApiError(err)) {
      showNotification(
        err.response ? 'Unable to load users list.' : 'Unable to connect to server.',
        'error',
      )
    }
  }
}

onMounted(() => {
  fetchTeamInfo()
  fetchUsers()
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
  margin-top: 0.8rem;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  align-items: start;
}
</style>
