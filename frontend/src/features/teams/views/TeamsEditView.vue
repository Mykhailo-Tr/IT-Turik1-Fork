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

    <ui-card v-if="loading" class="state-card text-muted">Loading team editor...</ui-card>
    <ui-card v-else-if="loadError" class="state-card text-error">{{ loadError }}</ui-card>

    <template v-else-if="team">
      <div class="workspace-grid">
        <ui-card class="panel form-panel">
          <header class="panel-head">
            <h2>Team profile settings</h2>
            <span v-if="isCaptain" class="status-badge">Captain access</span>
          </header>

          <p v-if="!isCaptain" class="notice error lock-note">
            Only team captain can edit this team.
          </p>

          <form class="form-grid" @submit.prevent="saveTeam">
            <label class="form-label">
              Team name
              <ui-input v-model="form.name" required :disabled="!isCaptain || saveLoading" />
            </label>

            <label class="form-label">
              Team email
              <ui-input
                v-model="form.email"
                type="email"
                required
                :disabled="!isCaptain || saveLoading"
              />
            </label>

            <label class="form-label">
              Organization
              <ui-input v-model="form.organization" :disabled="!isCaptain || saveLoading" />
            </label>

            <label class="form-label">
              Telegram
              <ui-input
                v-model="form.contact_telegram"
                pattern="^@?[A-Za-z][A-Za-z0-9_]{4,31}$"
                title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
                :disabled="!isCaptain || saveLoading"
              />
            </label>

            <label class="form-label">
              Discord
              <ui-input
                v-model="form.contact_discord"
                pattern="^@?(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?$"
                title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
                :disabled="!isCaptain || saveLoading"
              />
            </label>

            <div class="form-actions full-width">
              <ui-button type="submit" :disabled="!isCaptain || saveLoading">
                {{ saveLoading ? 'Saving...' : 'Save changes' }}
              </ui-button>
              <ui-button asLink variant="outline" :to="`/teams/${team.id}`">Cancel</ui-button>
            </div>
          </form>
        </ui-card>

        <ui-card class="panel members-panel">
          <header class="panel-head">
            <h2>Members management</h2>
            <span class="text-muted">{{ team.members.length }} people</span>
          </header>

          <label class="form-label member-search">
            Search members
            <ui-input v-model="memberSearch" placeholder="Search by username or email" />
          </label>

          <div class="member-list">
            <article
              v-for="member in filteredMembers"
              :key="`member-${member.id}`"
              class="member-row"
            >
              <div>
                <p class="member-name">{{ member.username }}</p>
                <p class="text-muted member-email">{{ member.email }}</p>
              </div>

              <div class="member-actions">
                <ui-badge v-if="member.id === team.captain_id" variant="green" value="Captain" />
                <ui-button
                  v-else-if="isCaptain"
                  variant="danger"
                  size="sm"
                  :disabled="kickLoadingByUser[member.id]"
                  @click="removeMember(member)"
                >
                  {{ kickLoadingByUser[member.id] ? 'Removing...' : 'Remove' }}
                </ui-button>
              </div>
            </article>
          </div>
          <div v-if="isCaptain" class="add-member-box">
            <h3>Invitations status</h3>
            <p v-if="!team.invitations?.length" class="text-muted">No invitations yet.</p>
            <div v-else class="member-list">
              <article
                v-for="invitation in team.invitations"
                :key="`inv-${invitation.id}`"
                class="member-row"
              >
                <div>
                  <p class="member-name">{{ invitation.user.username }}</p>
                  <p class="text-muted member-email">{{ invitation.user.email }}</p>
                </div>
                <!-- if declined red -->
                <span v-if="invitation.status === 'declined'" class="status status--declined">
                  {{ invitation.status }}
                </span>
                <span v-else class="status status--source">{{ invitation.status }}</span>
              </article>
            </div>
          </div>

          <p v-if="filteredMembers.length === 0" class="text-muted member-note">
            No members match your search.
          </p>

          <div v-if="isCaptain" class="add-member-box">
            <h3>Invite user</h3>

            <label class="form-label">
              Select user
              <ui-select :options="userOptions" v-model="addMemberSelection" />
            </label>

            <p v-if="availableUsers.length === 0" class="text-muted">No available users to add.</p>

            <ui-button @click="addMember" :disabled="addMemberLoading">
              {{ addMemberLoading ? 'Sending...' : 'Send invitation' }}
            </ui-button>
          </div>
        </ui-card>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import UiBadge from '@/components/UiBadge.vue'
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiInput from '@/components/UiInput.vue'
import UiSelect from '@/components/UiSelect.vue'
import { useTeamsEditPage } from '@/features/teams/composables/useTeamsEditPage'
import { computed } from 'vue'

const userOptions = computed(() => [
  { value: '', label: 'Select user' },
  ...availableUsers.value.map((user) => ({
    value: String(user.id),
    label: `${user.username} (${user.email})`,
  })),
])

const {
  addMember,
  addMemberLoading,
  addMemberSelection,
  availableUsers,
  filteredMembers,
  form,
  isCaptain,
  kickLoadingByUser,
  loadError,
  loading,
  memberSearch,
  removeMember,
  saveLoading,
  saveTeam,
  team,
} = useTeamsEditPage()
</script>

<style scoped src="../styles/teams-edit-view.css"></style>
<style scoped src="../styles/status-tags.css"></style>
