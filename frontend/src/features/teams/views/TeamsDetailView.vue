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
            class="contact-pill"
            :href="telegramLink(team.contact_telegram)"
            target="_blank"
            rel="noopener noreferrer"
          >
            <telegram-icon />
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
            <discord-icon />
            <span>{{ team.contact_discord }}</span>
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
        <ui-card class="panel info-panel">
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
        </ui-card>

        <ui-card class="panel members-panel">
          <header class="panel-head">
            <h2>Members</h2>
            <span class="text-muted">{{ team.members.length }} accepted</span>
          </header>

          <label class="form-label member-search">
            Search members
            <ui-input v-model="memberSearch" placeholder="Search by username or email" />
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
                      <ui-badge variant="green" value="Captain" />
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
                      <ui-badge variant="green" value="Captain" />
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
                      <ui-badge variant="green" value="Captain" />
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
                      <ui-badge variant="green" value="Captain" />
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
        </ui-card>
      </div>

      <ui-card v-if="isCaptain" class="manage-zone">
        <div class="manage-row">
          <div>
            <h3>Edit team</h3>
            <p class="text-muted">Update team profile and manage members in edit workspace.</p>
          </div>
          <ui-button asLink variant="outline" size="sm" :to="`/teams/${team.id}/edit`"
            >Edit team</ui-button
          >
        </div>

        <div class="danger-zone-header">
          <danger-icon />
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
            <ui-button
              size="sm"
              variant="warning"
              :disabled="visibilityLoading"
              @click="openVisibilityModal"
            >
              Change visibility
            </ui-button>
          </div>

          <div class="manage-row danger">
            <div>
              <h3>Delete team</h3>
              <p class="text-muted">
                This action permanently deletes the team and cannot be undone.
              </p>
            </div>
            <ui-button
              size="sm"
              variant="danger"
              :disabled="deleteTeamLoading"
              @click="openDeleteModal"
            >
              Delete team
            </ui-button>
          </div>
        </div>
      </ui-card>
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
            <ui-input
              v-model="selectedVisibility"
              type="radio"
              name="visibility"
              :value="true"
              :disabled="visibilityLoading"
            />
            <div class="visibility-option-content">
              <div class="visibility-option-header">
                <eye-in-circle />
                <strong>Public</strong>
              </div>
              <p>Anyone can find and request to join this team.</p>
            </div>
          </label>

          <label class="visibility-option" :class="{ selected: selectedVisibility === false }">
            <ui-input
              v-model="selectedVisibility"
              type="radio"
              name="visibility"
              :value="false"
              :disabled="visibilityLoading"
            />
            <div class="visibility-option-content">
              <div class="visibility-option-header">
                <lock-icon />
                <strong>Private</strong>
              </div>
              <p>Only invited members can find and access this team.</p>
            </div>
          </label>
        </div>

        <div v-if="selectedVisibility !== team?.is_public" class="visibility-confirm-note">
          <danger-icon />

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
          <ui-button
            size="sm"
            variant="outline"
            class="btn-cancel"
            type="button"
            :disabled="visibilityLoading"
            @click="closeVisibilityModal"
          >
            Cancel
          </ui-button>
          <ui-button
            variant="warning"
            size="sm"
            class="btn-warning"
            type="button"
            :disabled="visibilityLoading || selectedVisibility === team?.is_public"
            @click="confirmChangeVisibility"
          >
            {{ visibilityLoading ? 'Saving...' : 'Confirm change' }}
          </ui-button>
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

        <ui-input
          v-model="deleteConfirmInput"
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
import DangerIcon from '@/icons/DangerIcon.vue'
import DiscordIcon from '@/icons/DiscordIcon.vue'
import EyeInCircle from '@/icons/EyeInCircle.vue'
import LockIcon from '@/icons/LockIcon.vue'
import TelegramIcon from '@/icons/TelegramIcon.vue'
import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiCard from '@/components/UiCard.vue'
import UiBadge from '@/components/UiBadge.vue'

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
