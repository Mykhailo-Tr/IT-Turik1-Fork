<template>
  <section class="page-shell teams-page">
    <article class="card header-card">
      <p class="section-eyebrow">Teams</p>
      <h1 class="section-title">Team directory</h1>
      <p class="section-subtitle">Open a team workspace to view details, edit info, and manage members.</p>
      <div class="hero-actions">
        <router-link to="/teams/create" class="btn-primary manage-link">Create new team</router-link>
        <span class="meta-pill">Total teams: {{ teams.length }}</span>
      </div>
    </article>

    <div v-if="loading" class="card state-card text-muted">Loading teams...</div>

    <template v-else>
      <article class="card teams-card">
        <header class="section-head">
          <h2>Invitations</h2>
          <span class="text-muted">{{ pendingInboxInvitations.length }} pending</span>
        </header>

        <p v-if="inboxLoading" class="text-muted">Loading invitations...</p>
        <p v-else-if="pendingInboxInvitations.length === 0" class="text-muted">No pending invitations.</p>
        <div v-else class="team-grid">
          <article v-for="invitation in pendingInboxInvitations" :key="`invite-${invitation.id}`" class="team-item">
            <div class="team-meta">
              <h3>{{ invitation.team.name }}</h3>
              <span class="status status--invited">invited</span>
            </div>
            <p class="text-muted">Invited by: {{ invitation.invited_by?.username || 'Unknown user' }}</p>
            <div class="row-actions">
              <button
                type="button"
                class="btn-soft"
                :disabled="invitationActionLoading[invitation.id]"
                @click="respondToInvitation(invitation.id, 'accept')"
              >
                Accept
              </button>
              <button
                type="button"
                class="btn-soft"
                :disabled="invitationActionLoading[invitation.id]"
                @click="respondToInvitation(invitation.id, 'decline')"
              >
                Decline
              </button>
            </div>
          </article>
        </div>
      </article>

      <article class="card teams-card">
        <header class="section-head">
          <h2>My teams</h2>
          <span class="text-muted">{{ myTeams.length }} joined</span>
        </header>

        <p v-if="myTeams.length === 0" class="text-muted">You are not a member of any team yet.</p>
        <div v-else class="team-grid">
          <article v-for="team in myTeamsPageItems" :key="`my-${team.id}`" class="team-item">
            <div class="team-meta">
              <h3>{{ team.name }}</h3>
              <span v-if="isCaptain(team)" class="status-badge">Captain</span>
            </div>
            <p class="text-muted">Visibility: {{ team.is_public ? 'Public' : 'Private' }}</p>
            <p class="text-muted">Captain: {{ captainName(team) }}</p>
            <p class="text-muted">Members: {{ team.members.length }}</p>
            <p v-if="team.my_invitation_status" class="text-muted">My invitation: {{ team.my_invitation_status }}</p>
            <p v-if="team.my_join_request_status" class="text-muted">My join request: {{ team.my_join_request_status }}</p>
            <router-link :to="`/teams/${team.id}`" class="btn-soft open-link">Open workspace</router-link>
          </article>
        </div>

        <div v-if="myPages > 1" class="pagination">
          <button class="btn-soft" :disabled="myPage === 1" @click="myPage -= 1" type="button">Prev</button>
          <span>Page {{ myPage }} / {{ myPages }}</span>
          <button class="btn-soft" :disabled="myPage === myPages" @click="myPage += 1" type="button">Next</button>
        </div>
      </article>

      <article class="card teams-card">
        <header class="section-head">
          <h2>Other teams</h2>
          <span class="text-muted">{{ otherTeams.length }} available</span>
        </header>

        <p v-if="otherTeams.length === 0" class="text-muted">No other teams available.</p>
        <div v-else class="team-grid">
          <article v-for="team in otherTeamsPageItems" :key="`other-${team.id}`" class="team-item">
            <div class="team-meta">
              <h3>{{ team.name }}</h3>
            </div>
            <p class="text-muted">Visibility: {{ team.is_public ? 'Public' : 'Private' }}</p>
            <p class="text-muted">Captain: {{ captainName(team) }}</p>
            <p class="text-muted">Members: {{ team.members.length }}</p>
            <p v-if="team.my_invitation_status" class="text-muted">My invitation: {{ team.my_invitation_status }}</p>
            <p v-if="team.my_join_request_status" class="text-muted">My join request: {{ team.my_join_request_status }}</p>
            <button
              v-if="team.can_request_to_join"
              type="button"
              class="btn-soft"
              :disabled="joinRequestLoadingByTeam[team.id]"
              @click="sendJoinRequest(team.id)"
            >
              {{ joinRequestLoadingByTeam[team.id] ? 'Sending...' : 'Request to join' }}
            </button>
            <router-link :to="`/teams/${team.id}`" class="btn-soft open-link">Open workspace</router-link>
          </article>
        </div>

        <div v-if="otherPages > 1" class="pagination">
          <button class="btn-soft" :disabled="otherPage === 1" @click="otherPage -= 1" type="button">Prev</button>
          <span>Page {{ otherPage }} / {{ otherPages }}</span>
          <button class="btn-soft" :disabled="otherPage === otherPages" @click="otherPage += 1" type="button">Next</button>
        </div>
      </article>
    </template>
  </section>
</template>

<script setup>
import { useTeamsViewPage } from '@/features/teams/composables/useTeamsViewPage'

const {
  captainName,
  inboxLoading,
  invitationActionLoading,
  isCaptain,
  joinRequestLoadingByTeam,
  loading,
  myPage,
  myPages,
  myTeams,
  myTeamsPageItems,
  otherPage,
  otherPages,
  otherTeams,
  otherTeamsPageItems,
  pendingInboxInvitations,
  respondToInvitation,
  sendJoinRequest,
  teams,
} = useTeamsViewPage()
</script>

<style scoped src="../styles/teams-view.css"></style>
<style scoped src="../styles/status-tags.css"></style>


