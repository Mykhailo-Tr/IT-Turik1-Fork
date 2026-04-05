<!-- TODO: split into smaller components -->

<template>
  <section class="page-shell teams-detail-page">
    <ui-card class="hero-card">
      <div class="hero-top">
        <div>
          <p class="section-eyebrow">Team workspace</p>
          <h1 class="section-title">{{ team?.name || 'Team details' }}</h1>
        </div>

        <div class="hero-contacts">
          <a
            v-if="team?.contact_telegram"
            :href="telegramLink(team.contact_telegram)"
            class="contact-pill"
          >
            <telegram-icon class="contact-icon" />
            <ui-badge>@{{ team?.contact_telegram }}</ui-badge>
          </a>

          <span v-else class="contact-pill muted">No Telegram</span>

          <a
            v-if="team?.contact_discord"
            class="contact-pill"
            :href="discordLink(team.contact_discord)"
          >
            <discord-icon class="contact-icon" />
            <ui-badge>{{ team.contact_discord }}</ui-badge>
          </a>

          <span v-else class="contact-pill muted">No Discord</span>
        </div>
      </div>

      <div class="hero-actions">
        <ui-button asLink variant="outline" size="sm" to="/teams">Back to teams</ui-button>
      </div>
    </ui-card>

    <ui-card v-if="loading" class="state-card text-muted">Loading team workspace...</ui-card>
    <ui-card v-else-if="loadError" class="state-card text-error">{{ loadError }}</ui-card>

    <template v-else-if="team">
      <div class="workspace-grid">
        <team-base-info
          :team="team"
          :is-captain="isCaptain"
          @deleted="router.push('/teams')"
          @leave="router.push('/teams')"
        />

        <team-members
          :team="team"
          :is-captain="isCaptain"
          @update-team="(newTeamValue) => (team = newTeamValue)"
        />
      </div>

      <team-manage-zone
        :team="team"
        :is-captain="isCaptain"
        @update-team="(newTeamValue) => (team = newTeamValue)"
      />
    </template>
  </section>
</template>

<script setup lang="ts">
import DiscordIcon from '@/icons/DiscordIcon.vue'
import TelegramIcon from '@/icons/TelegramIcon.vue'
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import TeamBaseInfo from '../components/teamDetail/TeamBaseInfo.vue'
import { useRoute, useRouter } from 'vue-router'
import { computed, onMounted, ref } from 'vue'
import { isApiError } from '@/services/apiClient'
import $api from '@/services'
import type { GetTeamInfoResponse } from '@/services/teams/types'
import TeamMembers from '../components/teamDetail/TeamMembers.vue'
import { discordLink, telegramLink } from '../lib/team-links'
import { useAuth } from '@/composables/useAuth'
import UiBadge from '@/components/UiBadge.vue'
import TeamManageZone from '../components/teamDetail/TeamManageZone.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuth()

const team = ref<GetTeamInfoResponse | null>(null)

const loadError = ref('')
const loading = ref(false)

const teamId = computed(() => Number(route.params.id))

const fetchTeamInfo = async () => {
  if (!teamId.value) {
    loadError.value = 'Invalid team id.'
    return false
  }

  try {
    const response = await $api.teams.getTeamInfo(teamId.value)

    team.value = response.data
    return true
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        if (err.response.status === 401) return router.push('/login')
        if (err.response.status === 404) {
          loadError.value = 'Team not found.'
          team.value = null
          return
        }

        loadError.value = 'Unable to load team information.'
      } else {
      }
    }
  }
}

const isCaptain = computed(() => team.value?.captain_id === auth.user.value?.id)

onMounted(() => {
  fetchTeamInfo()
})
</script>

<style scoped>
.hero-card {
  padding: 1.2rem;
}

.hero-card {
  background: linear-gradient(135deg, rgba(13, 148, 136, 0.14), rgba(15, 23, 42, 0.03)), #fff;
  border: 1px solid rgba(13, 148, 136, 0.22);
}

.hero-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.hero-contacts {
  display: grid;
  gap: 0.45rem;
  justify-items: end;
}

.contact-icon {
  width: 1.3rem;
  height: 1.3rem;
  color: var(--brand-700);
}

.contact-pill {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  text-decoration: none;
}

.hero-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-top: 0.8rem;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 0.95fr 1.25fr;
  gap: 1rem;
  align-items: start;
}

.panel {
  border: 1px solid var(--line-soft);
}

@media (max-width: 1020px) {
  .hero-top {
    flex-direction: column;
  }

  .hero-contacts {
    justify-items: start;
  }

  .workspace-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .member-row,
  .manage-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .member-side {
    align-items: flex-start;
  }

  .status-tags {
    justify-content: flex-start;
  }
}
</style>
