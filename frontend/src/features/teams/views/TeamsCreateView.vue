<template>
  <section class="page-shell teams-page">
    <article class="card create-card">
      <p class="section-eyebrow">Teams</p>
      <h1 class="section-title">Create new team</h1>
      <p class="section-subtitle">Create a team and optionally add initial members.</p>
      <router-link to="/teams" class="back-link">Back to teams list</router-link>

      <form class="form-grid" @submit.prevent="handleCreateTeam">
        <label class="form-label">
          Team name
          <input v-model="createForm.name" class="input-control" type="text" required />
        </label>

        <label class="form-label">
          Team email
          <input v-model="createForm.email" class="input-control" type="email" required />
        </label>

        <label class="form-label">
          Organization
          <input v-model="createForm.organization" class="input-control" type="text" />
        </label>

        <label class="form-label toggle-field">
          <span>Team visibility</span>
          <span class="toggle-row">
            <input v-model="createForm.is_public" type="checkbox" />
            <span>{{ createForm.is_public ? 'Public' : 'Private' }}</span>
          </span>
        </label>

        <label class="form-label">
          Telegram
          <input
            v-model="createForm.contact_telegram"
            class="input-control"
            type="text"
            placeholder="@team_username"
            pattern="^@?[A-Za-z][A-Za-z0-9_]{4,31}$"
            title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
          />
        </label>

        <label class="form-label">
          Discord
          <input
            v-model="createForm.contact_discord"
            class="input-control"
            type="text"
            placeholder="team.username"
            pattern="^@?(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?$"
            title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
          />
        </label>

        <div class="full-width">
          <label class="form-label">
            Add initial members
            <input
              v-model="memberSearch"
              class="input-control"
              type="text"
              placeholder="Search by username, email, full name"
            />
          </label>

          <div class="member-picker">
            <label v-for="user in createCandidateUsers" :key="`create-${user.id}`" class="picker-item">
              <input v-model="createForm.member_ids" type="checkbox" :value="user.id" />
              <span>{{ user.username }} ({{ user.email }})</span>
            </label>
            <p v-if="createCandidateUsers.length === 0" class="text-muted empty-note">No users found.</p>
          </div>
        </div>

        <button class="btn-primary full-width" :disabled="createLoading" type="submit">
          {{ createLoading ? 'Creating...' : 'Create team' }}
        </button>
      </form>
    </article>
  </section>
</template>

<script setup>
import { useTeamsCreatePage } from '@/features/teams/composables/useTeamsCreatePage'

const {
  createCandidateUsers,
  createForm,
  createLoading,
  handleCreateTeam,
  memberSearch,
} = useTeamsCreatePage()
</script>

<style scoped src="../styles/teams-create-view.css"></style>


