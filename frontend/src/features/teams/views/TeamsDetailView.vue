<!-- TODO: split into smaller components -->

<template>
  <section class="page-shell teams-detail-page">
    <article class="card hero-card">
      <div class="hero-top">
        <div>
          <p class="section-eyebrow">Team workspace</p>
          <h1 class="section-title">{{ team?.name || 'Team details' }}</h1>
        </div>

        <div class="hero-contacts">
          <a
            v-if="team?.contact_telegram"
            class="contact-pill"
            :href="telegramLink(team.contact_telegram)"
            target="_blank"
            rel="noopener noreferrer"
          >
            <svg viewBox="0 0 24 24" class="contact-icon" aria-hidden="true">
              <path
                d="M9.04 15.57 8.9 19.47c.45 0 .64-.19.87-.43l2.09-1.98 4.34 3.17c.8.44 1.36.21 1.57-.74l2.85-13.37h.01c.25-1.15-.42-1.6-1.2-1.31L2.64 11.2c-1.12.44-1.1 1.07-.2 1.35l4.8 1.5L18.4 6.9c.53-.35 1.02-.16.62.2L9.04 15.57z"
                fill="currentColor"
              />
            </svg>
            <span>@{{ team.contact_telegram }}</span>
          </a>

          <span v-else class="contact-pill muted">No Telegram</span>

          <a
            v-if="team?.contact_discord"
            class="contact-pill"
            :href="discordLink(team.contact_discord)"
            target="_blank"
            rel="noopener noreferrer"
          >
            <svg viewBox="0 0 24 24" class="contact-icon" aria-hidden="true">
              <path
                d="M20.32 4.37A19.8 19.8 0 0 0 15.3 3l-.27.54a18.7 18.7 0 0 1 4.82 1.48c-2.97-1.39-6.16-2.1-9.36-2.05-3.2-.05-6.39.66-9.36 2.05a18.7 18.7 0 0 1 4.82-1.48L5.68 3A19.8 19.8 0 0 0 .66 4.37C-2.53 9.1-3.39 13.7-2.97 18.22a19.9 19.9 0 0 0 6.11 3.08l1.31-1.8c-.72-.27-1.4-.6-2.04-.98.17.12.36.23.55.34 3.84 2.1 8 2.1 11.84 0 .19-.11.38-.22.55-.34-.64.38-1.32.71-2.04.98l1.31 1.8a19.9 19.9 0 0 0 6.11-3.08c.5-5.29-.86-9.86-3.4-13.85ZM8.02 15.45c-1.2 0-2.17-1.1-2.17-2.45 0-1.36.95-2.45 2.17-2.45 1.22 0 2.2 1.1 2.17 2.45 0 1.35-.95 2.45-2.17 2.45Zm7.96 0c-1.2 0-2.17-1.1-2.17-2.45 0-1.36.95-2.45 2.17-2.45 1.22 0 2.2 1.1 2.17 2.45 0 1.35-.95 2.45-2.17 2.45Z"
                fill="currentColor"
              />
            </svg>
            <span>{{ team.contact_discord }}</span>
          </a>

          <span v-else class="contact-pill muted">No Discord</span>
        </div>
      </div>

      <div class="hero-actions">
        <router-link to="/teams" class="btn-soft action-link">Back to teams</router-link>
      </div>
    </article>

    <div v-if="loading" class="card state-card text-muted">Loading team workspace...</div>
    <div v-else-if="loadError" class="card state-card text-error">{{ loadError }}</div>

    <template v-else-if="team">
      <div class="workspace-grid">
        <article class="card panel info-panel">
          <header class="panel-head">
            <h2>Team profile</h2>
            <span v-if="isCaptain" class="status-badge">You are captain</span>
          </header>

          <div class="info-grid">
            <div class="info-item">
              <span>Name</span>
              <strong>{{ team.name }}</strong>
            </div>
            <div class="info-item">
              <span>Email</span>
              <strong>{{ team.email }}</strong>
            </div>
            <div class="info-item">
              <span>Organization</span>
              <strong>{{ team.organization || '-' }}</strong>
            </div>
            <div class="info-item">
              <span>Captain</span>
              <strong>{{ captainName }}</strong>
            </div>
            <div class="info-item">
              <span>Members count</span>
              <strong>{{ team.members.length }}</strong>
            </div>
            <div class="info-item">
              <span>Visibility</span>
              <strong>{{ team.is_public ? 'Public' : 'Private' }}</strong>
            </div>
          </div>
          <div v-if="!isCaptain" class="status-line">
            <p v-if="team.my_invitation_status" class="text-muted">
              Your invitation status: {{ team.my_invitation_status }}
            </p>
            <p v-if="team.my_join_request_status" class="text-muted">
              Your join request status: {{ team.my_join_request_status }}
            </p>
          </div>
          <div class="info-actions">
            <button
              v-if="team.can_request_to_join"
              type="button"
              class="btn-soft"
              :disabled="joinRequestLoading"
              @click="sendJoinRequest"
            >
              {{ joinRequestLoading ? 'Sending...' : 'Request to join this team' }}
            </button>
            <button
              v-if="canLeaveTeam"
              type="button"
              class="btn-danger"
              :disabled="leaveTeamLoading"
              @click="openLeaveModal"
            >
              {{ leaveTeamLoading ? 'Leaving...' : 'Leave team' }}
            </button>
          </div>
        </article>

        <article class="card panel members-panel">
          <header class="panel-head">
            <h2>Members</h2>
            <span class="text-muted">{{ team.members.length }} accepted</span>
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

          <div class="members-sections">
            <section class="members-section">
              <header class="section-subhead">
                <h3>Members</h3>
                <span class="text-muted">{{ filteredMembers.length }} people</span>
              </header>

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
                  <div class="member-side">
                    <template v-if="member.id === team.captain_id">
                      <span class="captain-tag">Captain</span>
                    </template>
                    <template v-else>
                      <div class="status-tags">
                        <span class="status status--source">{{
                          statusByUserId?.[member.id]?.source || 'Member'
                        }}</span>
                      </div>
                    </template>
                  </div>
                </article>
              </div>

              <p v-if="filteredMembers.length === 0" class="text-muted member-note">
                No accepted members match your search.
              </p>
            </section>

            <section v-if="isCaptain" class="members-section">
              <header class="section-subhead">
                <h3>Join Requests</h3>
                <span class="text-muted">{{ filteredPendingJoinRequests.length }} pending</span>
              </header>

              <p v-if="filteredPendingJoinRequests.length === 0" class="text-muted member-note">
                No pending join requests.
              </p>

              <div v-else class="member-list">
                <article
                  v-for="joinRequest in filteredPendingJoinRequests"
                  :key="`join-request-${joinRequest.id}`"
                  class="member-row"
                >
                  <div>
                    <p class="member-name">{{ joinRequest.user.username }}</p>
                    <p class="text-muted member-email">{{ joinRequest.user.email }}</p>
                  </div>
                  <div class="member-side">
                    <template v-if="joinRequest.user.id === team.captain_id">
                      <span class="captain-tag">Captain</span>
                    </template>
                    <template v-else>
                      <div class="row-actions">
                        <button
                          type="button"
                          class="btn-soft"
                          :disabled="joinRequestActionLoading[joinRequest.id]"
                          @click="reviewJoinRequest(joinRequest.id, 'accept')"
                        >
                          Accept
                        </button>
                        <button
                          type="button"
                          class="btn-soft"
                          :disabled="joinRequestActionLoading[joinRequest.id]"
                          @click="reviewJoinRequest(joinRequest.id, 'decline')"
                        >
                          Decline
                        </button>
                      </div>
                    </template>
                  </div>
                </article>
              </div>
            </section>

            <section v-if="isCaptain" class="members-section">
              <header class="section-subhead">
                <h3>Invitations</h3>
                <span class="text-muted">
                  {{ filteredPendingInvitations.length }} awaiting response
                  <span v-if="filteredDeclinedInvitations.length"
                    >, {{ filteredDeclinedInvitations.length }} declined</span
                  >
                </span>
              </header>

              <p
                v-if="
                  filteredPendingInvitations.length === 0 &&
                  filteredDeclinedInvitations.length === 0
                "
                class="text-muted member-note"
              >
                No invitations yet.
              </p>

              <div v-else class="member-list invitations-list">
                <article
                  v-for="invitation in filteredPendingInvitations"
                  :key="`invitation-${invitation.id}`"
                  class="member-row"
                >
                  <div>
                    <p class="member-name">{{ invitation.user.username }}</p>
                    <p class="text-muted member-email">{{ invitation.user.email }}</p>
                  </div>
                  <div class="member-side">
                    <template v-if="invitation.user.id === team.captain_id">
                      <span class="captain-tag">Captain</span>
                    </template>
                    <template v-else>
                      <div class="status-tags">
                        <span class="status status--invited">invited</span>
                      </div>
                    </template>
                  </div>
                </article>

                <article
                  v-for="invitation in filteredDeclinedInvitations"
                  :key="`invitation-${invitation.id}`"
                  class="member-row"
                >
                  <div>
                    <p class="member-name">{{ invitation.user.username }}</p>
                    <p class="text-muted member-email">{{ invitation.user.email }}</p>
                  </div>
                  <div class="member-side">
                    <template v-if="invitation.user.id === team.captain_id">
                      <span class="captain-tag">Captain</span>
                    </template>
                    <template v-else>
                      <div class="status-tags">
                        <span class="status status--declined">declined</span>
                        <span class="status status--source">Invitation</span>
                      </div>
                      <div class="row-actions">
                        <button
                          type="button"
                          class="btn-soft"
                          :disabled="resendInvitationLoading[invitation.user.id]"
                          @click="resendInvitation(invitation.user.id)"
                        >
                          {{
                            resendInvitationLoading[invitation.user.id]
                              ? 'Resending...'
                              : 'Resend invitation'
                          }}
                        </button>
                      </div>
                    </template>
                  </div>
                </article>
              </div>
            </section>
          </div>
        </article>
      </div>

      <article v-if="isCaptain" class="card manage-zone">
        <div class="manage-row">
          <div>
            <h3>Edit team</h3>
            <p class="text-muted">Update team profile and manage members in edit workspace.</p>
          </div>
          <router-link :to="`/teams/${team.id}/edit`" class="btn-soft action-link action-btn"
            >Edit team</router-link
          >
        </div>

        <div class="danger-zone-header">
          <svg viewBox="0 0 24 24" class="danger-zone-icon" aria-hidden="true">
            <path
              d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              fill="none"
            />
          </svg>
          <span>Danger Zone</span>
        </div>

        <div class="danger-zone-box">
          <div class="manage-row danger">
            <div>
              <h3>Change visibility</h3>
              <p class="text-muted">
                This team is currently
                <span
                  class="visibility-badge"
                  :class="team.is_public ? 'visibility-public' : 'visibility-private'"
                >
                  {{ team.is_public ? 'Public' : 'Private' }} </span
                >.
                {{
                  team.is_public
                    ? 'Anyone can find and request to join this team.'
                    : 'Only invited members can see this team.'
                }}
              </p>
            </div>
            <button
              class="btn-warning"
              type="button"
              :disabled="visibilityLoading"
              @click="openVisibilityModal"
            >
              Change visibility
            </button>
          </div>

          <div class="manage-row danger">
            <div>
              <h3>Delete team</h3>
              <p class="text-muted">
                This action permanently deletes the team and cannot be undone.
              </p>
            </div>
            <button
              class="btn-danger"
              type="button"
              :disabled="deleteTeamLoading"
              @click="openDeleteModal"
            >
              Delete team
            </button>
          </div>
        </div>
      </article>
    </template>

    <div v-if="isLeaveModalOpen" class="modal-backdrop" @click.self="closeLeaveModal">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="leave-team-title">
        <h3 id="leave-team-title">Leave Team?</h3>
        <p class="modal-text">Are you sure you want to leave this team?</p>

        <div class="modal-actions">
          <button
            class="btn-cancel"
            type="button"
            :disabled="leaveTeamLoading"
            @click="closeLeaveModal"
          >
            Cancel
          </button>
          <button
            class="btn-danger"
            type="button"
            :disabled="leaveTeamLoading"
            @click="confirmLeaveTeam"
          >
            {{ leaveTeamLoading ? 'Leaving...' : 'Leave' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="isVisibilityModalOpen" class="modal-backdrop" @click.self="closeVisibilityModal">
      <div
        class="modal-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="visibility-modal-title"
      >
        <h3 id="visibility-modal-title">Change team visibility</h3>
        <p class="modal-text">
          Select the new visibility for <code>{{ team?.name }}</code
          >. This affects who can discover and join your team.
        </p>

        <div class="visibility-options">
          <label class="visibility-option" :class="{ selected: selectedVisibility === true }">
            <input
              v-model="selectedVisibility"
              type="radio"
              name="visibility"
              :value="true"
              :disabled="visibilityLoading"
            />
            <div class="visibility-option-content">
              <div class="visibility-option-header">
                <svg viewBox="0 0 24 24" class="visibility-option-icon" aria-hidden="true">
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="2"
                    fill="none"
                  />
                  <path
                    d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z"
                    stroke="currentColor"
                    stroke-width="2"
                    fill="none"
                  />
                  <circle cx="12" cy="12" r="3" fill="currentColor" />
                </svg>
                <strong>Public</strong>
              </div>
              <p>Anyone can find and request to join this team.</p>
            </div>
          </label>

          <label class="visibility-option" :class="{ selected: selectedVisibility === false }">
            <input
              v-model="selectedVisibility"
              type="radio"
              name="visibility"
              :value="false"
              :disabled="visibilityLoading"
            />
            <div class="visibility-option-content">
              <div class="visibility-option-header">
                <svg viewBox="0 0 24 24" class="visibility-option-icon" aria-hidden="true">
                  <rect
                    x="3"
                    y="11"
                    width="18"
                    height="11"
                    rx="2"
                    ry="2"
                    stroke="currentColor"
                    stroke-width="2"
                    fill="none"
                  />
                  <path
                    d="M7 11V7a5 5 0 0 1 10 0v4"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    fill="none"
                  />
                </svg>
                <strong>Private</strong>
              </div>
              <p>Only invited members can find and access this team.</p>
            </div>
          </label>
        </div>

        <div v-if="selectedVisibility !== team?.is_public" class="visibility-confirm-note">
          <svg viewBox="0 0 24 24" class="note-icon" aria-hidden="true">
            <path
              d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              fill="none"
            />
          </svg>
          <span>
            You are about to change this team from
            <strong>{{ team?.is_public ? 'Public' : 'Private' }}</strong>
            to
            <strong>{{ selectedVisibility ? 'Public' : 'Private' }}</strong
            >.
          </span>
        </div>

        <p v-if="visibilityError" class="text-error modal-error">{{ visibilityError }}</p>

        <div class="modal-actions">
          <button
            class="btn-cancel"
            type="button"
            :disabled="visibilityLoading"
            @click="closeVisibilityModal"
          >
            Cancel
          </button>
          <button
            class="btn-warning"
            type="button"
            :disabled="visibilityLoading || selectedVisibility === team?.is_public"
            @click="confirmChangeVisibility"
          >
            {{ visibilityLoading ? 'Saving...' : 'Confirm change' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="isDeleteModalOpen" class="modal-backdrop" @click.self="closeDeleteModal">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="delete-team-title">
        <h3 id="delete-team-title">Delete team</h3>
        <p class="modal-text">
          This action cannot be undone. Enter
          <code>{{ expectedDeleteText }}</code>
          to confirm.
        </p>

        <input
          v-model="deleteConfirmInput"
          class="input-control"
          type="text"
          :placeholder="expectedDeleteText"
          :disabled="deleteTeamLoading"
        />

        <p v-if="deleteError" class="text-error modal-error">{{ deleteError }}</p>

        <div class="modal-actions">
          <button
            class="btn-cancel"
            type="button"
            :disabled="deleteTeamLoading"
            @click="closeDeleteModal"
          >
            Cancel
          </button>
          <button
            class="btn-danger"
            type="button"
            :disabled="!canDeleteTeam"
            @click="confirmDeleteTeam"
          >
            {{ deleteTeamLoading ? 'Deleting...' : 'Delete permanently' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useTeamsDetailWorkspace } from '@/features/teams/composables/useTeamsDetailWorkspace'

const {
  canDeleteTeam,
  canLeaveTeam,
  captainName,
  closeDeleteModal,
  closeLeaveModal,
  closeVisibilityModal,
  confirmChangeVisibility,
  confirmDeleteTeam,
  confirmLeaveTeam,
  deleteConfirmInput,
  deleteError,
  deleteTeamLoading,
  discordLink,
  expectedDeleteText,
  filteredDeclinedInvitations,
  filteredMembers,
  filteredPendingInvitations,
  filteredPendingJoinRequests,
  isCaptain,
  isDeleteModalOpen,
  isLeaveModalOpen,
  isVisibilityModalOpen,
  joinRequestActionLoading,
  joinRequestLoading,
  leaveTeamLoading,
  loadError,
  loading,
  memberSearch,
  openDeleteModal,
  openLeaveModal,
  openVisibilityModal,
  resendInvitation,
  resendInvitationLoading,
  reviewJoinRequest,
  selectedVisibility,
  sendJoinRequest,
  statusByUserId,
  team,
  telegramLink,
  visibilityError,
  visibilityLoading,
} = useTeamsDetailWorkspace()
</script>

<style scoped src="../styles/teams-detail-view.css"></style>
<style scoped src="../styles/status-tags.css"></style>
