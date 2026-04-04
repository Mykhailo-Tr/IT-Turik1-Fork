<template>
  <section class="page-shell teams-page">
    <ui-card class="header-card">
      <p class="section-eyebrow">Teams</p>
      <h1 class="section-title">Team directory</h1>
      <p class="section-subtitle">
        Open a team workspace to view details, edit info, and manage members.
      </p>
      <div class="hero-actions">
        <ui-button asLink to="/teams/create" class="manage-link">Create new team</ui-button>
        <span class="meta-pill">Total teams: {{ teams.length }}</span>
      </div>
    </ui-card>

    <ui-card v-if="loading" class="state-card text-muted">Loading teams...</ui-card>

    <template v-else>
      <ui-card class="teams-card">
        <header class="section-head">
          <h2>Invitations</h2>
          <span class="text-muted">{{ pendingInboxInvitations.length }} pending</span>
        </header>

        <p v-if="inboxLoading" class="text-muted">Loading invitations...</p>
        <p v-else-if="pendingInboxInvitations.length === 0" class="text-muted">
          No pending invitations.
        </p>
        <div v-else class="team-grid">
          <article
            v-for="invitation in pendingInboxInvitations"
            :key="`invite-${invitation.id}`"
            class="team-item"
          >
            <div class="team-meta">
              <h3>{{ invitation.team.name }}</h3>
              <span class="status status--invited">invited</span>
            </div>
            <p class="text-muted">
              Invited by: {{ invitation.invited_by?.username || 'Unknown user' }}
            </p>
            <div class="row-actions">
              <ui-button
                size="sm"
                :disabled="invitationActionLoading[invitation.id]"
                @click="respondToInvitation(invitation.id, 'accept')"
              >
                Accept
              </ui-button>
              <ui-button
                size="sm"
                variant="outline"
                :disabled="invitationActionLoading[invitation.id]"
                @click="respondToInvitation(invitation.id, 'decline')"
              >
                Decline
              </ui-button>
            </div>
          </article>
        </div>
      </ui-card>

      <ui-card class="teams-card">
        <header class="section-head">
          <h2>My teams</h2>
          <span class="text-muted">{{ myTeams.length }} joined</span>
        </header>

        <p v-if="myTeams.length === 0" class="text-muted">You are not a member of any team yet.</p>
        <div v-else class="team-grid">
          <ui-card v-for="team in myTeamsPageItems" :key="`my-${team.id}`" class="team-item">
            <div class="team-meta">
              <h3>{{ team.name }}</h3>
              <ui-badge v-if="isCaptain(team)" variant="blue">Captain</ui-badge>
            </div>
            <p class="text-muted">Visibility: {{ team.is_public ? 'Public' : 'Private' }}</p>
            <p class="text-muted">Captain: {{ captainName(team) }}</p>
            <p class="text-muted">Members: {{ team.members.length }}</p>
            <p v-if="team.my_invitation_status" class="text-muted">
              My invitation: {{ team.my_invitation_status }}
            </p>
            <p v-if="team.my_join_request_status" class="text-muted">
              My join request: {{ team.my_join_request_status }}
            </p>
            <ui-button asLink variant="outline" size="sm" :to="`/teams/${team.id}`"
              >Open workspace</ui-button
            >
          </ui-card>
        </div>

        <div v-if="myPages > 1" class="pagination">
          <button class="btn-soft" :disabled="myPage === 1" @click="myPage -= 1" type="button">
            Prev
          </button>
          <span>Page {{ myPage }} / {{ myPages }}</span>
          <button
            class="btn-soft"
            :disabled="myPage === myPages"
            @click="myPage += 1"
            type="button"
          >
            Next
          </button>
        </div>
      </ui-card>

      <ui-card class="teams-card">
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
            <p v-if="team.my_invitation_status" class="text-muted">
              My invitation: {{ team.my_invitation_status }}
            </p>
            <p v-if="team.my_join_request_status" class="text-muted">
              My join request: {{ team.my_join_request_status }}
            </p>
            <button
              v-if="team.can_request_to_join"
              type="button"
              class="btn-soft"
              :disabled="joinRequestLoadingByTeam[team.id]"
              @click="sendJoinRequest(team.id)"
            >
              {{ joinRequestLoadingByTeam[team.id] ? 'Sending...' : 'Request to join' }}
            </button>
            <ui-button asLink variant="outline" size="sm" :to="`/teams/${team.id}`"
              >Open workspace</ui-button
            >
          </article>
        </div>

        <div v-if="otherPages > 1" class="pagination">
          <button
            class="btn-soft"
            :disabled="otherPage === 1"
            @click="otherPage -= 1"
            type="button"
          >
            Prev
          </button>
          <span>Page {{ otherPage }} / {{ otherPages }}</span>
          <button
            class="btn-soft"
            :disabled="otherPage === otherPages"
            @click="otherPage += 1"
            type="button"
          >
            Next
          </button>
        </div>
      </ui-card>
    </template>
  </section>
</template>

<script setup lang="ts">
import UiBadge from '@/components/UiBadge.vue'
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
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
