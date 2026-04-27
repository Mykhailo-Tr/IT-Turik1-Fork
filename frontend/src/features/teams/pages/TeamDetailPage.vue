<template>
  <section class="page-shell teams-detail-page">
    <ui-card class="hero-card">
      <template #header>
        <div class="hero-top">
          <div>
            <p class="section-eyebrow">Team workspace</p>
            <ui-skeleton-loader class="section-title" :loading="isInfoLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" height="30px" width="200px" />
              </template>

              <h1 class="section-title" :title="team?.name">
                {{ truncateText(team?.name ?? 'Team details', 45) }}
              </h1>
            </ui-skeleton-loader>
          </div>

          <div class="hero-contacts">
            <ui-skeleton-loader :loading="isInfoLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" width="100px" />
              </template>
              <a
                v-if="team?.contact_telegram"
                :href="telegramLink(team.contact_telegram)"
                class="contact-pill"
              >
                <telegram-icon class="contact-icon" />

                <ui-badge>@{{ team?.contact_telegram }}</ui-badge>
              </a>
              <span v-else class="contact-pill muted">No Telegram</span>
            </ui-skeleton-loader>

            <ui-skeleton-loader :loading="isInfoLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" width="100px" />
              </template>
              <a
                v-if="team?.contact_discord"
                class="contact-pill"
                :href="discordLink(team.contact_discord)"
              >
                <discord-icon class="contact-icon" />
                <ui-badge>{{ team.contact_discord }}</ui-badge>
              </a>

              <span v-else class="contact-pill muted">No Discord</span>
            </ui-skeleton-loader>
          </div>
        </div>
      </template>

      <template #footer>
        <div class="hero-actions">
          <ui-button asLink variant="secondary" size="sm" to="/teams">Back to teams</ui-button>
        </div>
      </template>
    </ui-card>

    <div class="workspace-grid">
      <team-base-info
        :team="team"
        :loading="isInfoLoading"
        :loading-error="isInfoLoadingError"
        :is-captain="isCaptain"
        @deleted="router.push('/teams')"
        @leave="router.push('/teams')"
      />

      <ui-card class="panel">
        <div style="display: flex; flex-direction: column; gap: 20px">
          <ui-input
            v-model="searchInput"
            placeholder="Search by username or email"
            :disabled="isInfoLoading || isInfoLoadingError"
          />

          <team-members
            :team="team"
            :user="user"
            :search-filter="searchInput"
            :loading-error="isInfoLoadingError"
            :loading="isInfoLoading || isProfileLoading"
            :is-captain="isCaptain"
          />

          <template v-if="isCaptain && !isInfoLoading">
            <team-join-requests :search-filter="searchInput" :is-captain="isCaptain" />
            <team-invitations :search-filter="searchInput" :is-captain="isCaptain" />
          </template>
        </div>
      </ui-card>
    </div>

    <ui-skeleton-loader :loading="isInfoLoading">
      <team-manage-zone
        :team="team"
        :loading="isInfoLoading"
        :is-captain="isCaptain"
        @update-team="(newTeamValue) => (team = newTeamValue)"
      />
    </ui-skeleton-loader>
  </section>
</template>

<script setup lang="ts">
import DiscordIcon from '@/icons/DiscordIcon.vue'
import TelegramIcon from '@/icons/TelegramIcon.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import TeamBaseInfo from '../components/team-detail/TeamBaseInfo.vue'
import TeamMembers from '../components/team-detail/TeamMembers.vue'
import TeamManageZone from '../components/team-detail/TeamManageZone.vue'
import TeamJoinRequests from '../components/team-detail/TeamJoinRequests.vue'
import TeamInvitations from '../components/team-detail/TeamInvitations.vue'
import { useRoute, useRouter } from 'vue-router'
import { computed, ref } from 'vue'
import { discordLink, telegramLink } from '../lib/team-links'
import UiBadge from '@/components/ui/UiBadge.vue'
import { useTeamInfo } from '@/api/queries/teams'
import { useProfile } from '@/api/queries/accounts'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'

import UiInput from '@/components/ui/UiInput.vue'
import { truncateText } from '@/lib/utils'

const router = useRouter()
const route = useRoute()

const searchInput = ref('')
const { data: user, isLoading: isProfileLoading } = useProfile()
const {
  data: team,
  isLoading: isInfoLoading,
  isLoadingError: isInfoLoadingError,
} = useTeamInfo({ id: Number(route.params.id) })

const isCaptain = computed(() => team.value?.captain_id === user.value?.id)
</script>

<style scoped>
.hero-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.hero-contacts {
  display: flex;
  flex-direction: column;
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
}

.hero-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 0.95fr 1.25fr;
  gap: 1rem;
}

.panel {
  border: 1px solid var(--line-soft);
}

@media (max-width: 720px) {
  .hero-contacts {
    justify-items: start;
  }

  .workspace-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .member-side {
    align-items: flex-start;
  }

  .status-tags {
    justify-content: flex-start;
  }
}
</style>
