<template>
  <section class="page-shell teams-edit-page">
    <article class="card hero-card">
      <p class="section-eyebrow">Team workspace</p>
      <h1 class="section-title">Edit {{ team?.name || 'team' }}</h1>
      <div class="hero-actions">
        <router-link :to="team ? `/teams/${team.id}` : '/teams'" class="btn-soft action-link">Back to team</router-link>
      </div>
    </article>

    <div v-if="loading" class="card state-card text-muted">Loading team editor...</div>
    <div v-else-if="loadError" class="card state-card text-error">{{ loadError }}</div>

    <template v-else-if="team">
      <div class="workspace-grid">
        <article class="card panel form-panel">
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
              <input v-model="form.name" class="input-control" type="text" required :disabled="!isCaptain || saveLoading" />
            </label>

            <label class="form-label">
              Team email
              <input
                v-model="form.email"
                class="input-control"
                type="email"
                required
                :disabled="!isCaptain || saveLoading"
              />
            </label>

            <label class="form-label">
              Organization
              <input v-model="form.organization" class="input-control" type="text" :disabled="!isCaptain || saveLoading" />
            </label>

            <label class="form-label">
              Telegram
              <input
                v-model="form.contact_telegram"
                class="input-control"
                type="text"
                pattern="^@?[A-Za-z][A-Za-z0-9_]{4,31}$"
                title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
                :disabled="!isCaptain || saveLoading"
              />
            </label>

            <label class="form-label">
              Discord
              <input
                v-model="form.contact_discord"
                class="input-control"
                type="text"
                pattern="^@?(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?$"
                title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
                :disabled="!isCaptain || saveLoading"
              />
            </label>

            <div class="form-actions full-width">
              <button class="btn-primary" type="submit" :disabled="!isCaptain || saveLoading">
                {{ saveLoading ? 'Saving...' : 'Save changes' }}
              </button>
              <router-link :to="`/teams/${team.id}`" class="btn-soft action-link">Cancel</router-link>
            </div>
          </form>
        </article>

        <article class="card panel members-panel">
          <header class="panel-head">
            <h2>Members management</h2>
            <span class="text-muted">{{ team.members.length }} people</span>
          </header>

          <label class="form-label member-search">
            Search members
            <input
              v-model="memberSearch"
              class="input-control"
              type="text"
              placeholder="Search by username or email"
            />
          </label>

          <div class="member-list">
            <article v-for="member in filteredMembers" :key="`member-${member.id}`" class="member-row">
              <div>
                <p class="member-name">{{ member.username }}</p>
                <p class="text-muted member-email">{{ member.email }}</p>
              </div>

              <div class="member-actions">
                <span v-if="member.id === team.captain_id" class="captain-tag">Captain</span>
                <button
                  v-else-if="isCaptain"
                  type="button"
                  class="btn-danger btn-small"
                  :disabled="kickLoadingByUser[member.id]"
                  @click="removeMember(member)"
                >
                  {{ kickLoadingByUser[member.id] ? 'Removing...' : 'Remove' }}
                </button>
              </div>
            </article>
          </div>
          <div v-if="isCaptain" class="add-member-box">
            <h3>Invitations status</h3>
            <p v-if="!team.invitations?.length" class="text-muted">No invitations yet.</p>
            <div v-else class="member-list">
              <article v-for="invitation in team.invitations" :key="`inv-${invitation.id}`" class="member-row">
                <div>
                  <p class="member-name">{{ invitation.user.username }}</p>
                  <p class="text-muted member-email">{{ invitation.user.email }}</p>
                </div>
                <!-- if declined red -->
                <span v-if="invitation.status === 'declined'" class="status-tag status-declined">
                  {{ invitation.status }}
                </span>
                <span v-else class="captain-tag">{{ invitation.status }}</span>
              </article>
            </div>
          </div>

          <p v-if="filteredMembers.length === 0" class="text-muted member-note">No members match your search.</p>

          <div v-if="isCaptain" class="add-member-box">
            <h3>Invite user</h3>

            <label class="form-label">
              Select user
              <select v-model="addMemberSelection" class="select-control">
                <option value="">Select user</option>
                <option v-for="user in availableUsers" :key="`add-${user.id}`" :value="String(user.id)">
                  {{ user.username }} ({{ user.email }})
                </option>
              </select>
            </label>

            <p v-if="availableUsers.length === 0" class="text-muted">No available users to add.</p>

            <button class="btn-primary" type="button" @click="addMember" :disabled="addMemberLoading">
              {{ addMemberLoading ? 'Sending...' : 'Send invitation' }}
            </button>
          </div>


        </article>
      </div>
    </template>
  </section>
</template>

<script setup>
import { useTeamsEditPage } from '@/features/teams/composables/useTeamsEditPage'

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


