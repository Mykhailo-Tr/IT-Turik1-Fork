<template>
  <ui-card class="panel members-panel">
    <header class="panel-head">
      <h2>Members</h2>
      <span class="text-muted">{{ props.team.members.length }} accepted</span>
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
          <ui-card
            v-for="member in filteredMembers"
            :key="`member-${member.id}`"
            class="member-row"
          >
            <div>
              <p class="member-name">{{ member.username }}</p>
              <p class="text-muted member-email">{{ member.email }}</p>
            </div>
            <div class="member-side">
              <ui-badge v-if="member.id === props.team.captain_id" variant="green"
                >Captain</ui-badge
              >
              <template v-else>
                <ui-badge variant="gray">{{
                  statusByUserId[member.id]?.source || 'Member'
                }}</ui-badge>
              </template>
            </div>
          </ui-card>
        </div>

        <p v-if="filteredMembers.length === 0" class="text-muted member-note">
          No accepted members match your search.
        </p>
      </section>

      <section v-if="props.isCaptain" class="members-section">
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
              <ui-badge v-if="joinRequest.user.id === props.team.captain_id" variant="green"
                >Captain</ui-badge
              >
              <template v-else>
                <div class="row-actions">
                  <ui-button
                    size="sm"
                    :disabled="joinRequestsLoading[joinRequest.id]"
                    @click="reviewJoinRequest(joinRequest.id, 'accept')"
                  >
                    Accept
                  </ui-button>
                  <ui-button
                    variant="outline"
                    size="sm"
                    :disabled="joinRequestsLoading[joinRequest.id]"
                    @click="reviewJoinRequest(joinRequest.id, 'decline')"
                  >
                    Decline
                  </ui-button>
                </div>
              </template>
            </div>
          </article>
        </div>
      </section>

      <section v-if="props.isCaptain" class="members-section">
        <header class="section-subhead">
          <h3>Invitations</h3>
          <span class="text-muted">
            {{ filteredPendingInvitations.length }} awaiting response
            <span v-if="filteredDeclinedInvitations.length">
              , {{ filteredDeclinedInvitations.length }} declined
            </span>
          </span>
        </header>

        <p
          v-if="filteredPendingInvitations.length === 0 && filteredDeclinedInvitations.length === 0"
          class="text-muted member-note"
        >
          No invitations yet.
        </p>

        <div v-else class="member-list invitations-list">
          <article
            v-for="invitation in filteredPendingInvitations"
            :key="`invitation-pending-${invitation.id}`"
            class="member-row"
          >
            <div>
              <p class="member-name">{{ invitation.user.username }}</p>
              <p class="text-muted member-email">{{ invitation.user.email }}</p>
            </div>
            <div class="member-side">
              <ui-badge v-if="invitation.user.id === props.team.captain_id" variant="green"
                >Captain</ui-badge
              >
              <template v-else>
                <div class="status-tags">
                  <span class="status status--invited">invited</span>
                </div>
              </template>
            </div>
          </article>

          <article
            v-for="invitation in filteredDeclinedInvitations"
            :key="`invitation-declined-${invitation.id}`"
            class="member-row"
          >
            <div>
              <p class="member-name">{{ invitation.user.username }}</p>
              <p class="text-muted member-email">{{ invitation.user.email }}</p>
            </div>
            <div class="member-side">
              <ui-badge v-if="invitation.user.id === props.team.captain_id" variant="green"
                >Captain</ui-badge
              >
              <template v-else>
                <div class="status-tags">
                  <ui-badge variant="red">Declined</ui-badge>
                  <ui-badge>Invatation</ui-badge>
                </div>
                <div class="row-actions">
                  <ui-button
                    variant="outline"
                    size="sm"
                    :disabled="resendInvitationsLoading[invitation.user.id]"
                    @click="resendInvitation(invitation.user.id)"
                  >
                    {{
                      resendInvitationsLoading[invitation.user.id]
                        ? 'Resending...'
                        : 'Resend invitation'
                    }}
                  </ui-button>
                </div>
              </template>
            </div>
          </article>
        </div>
      </section>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/UiBadge.vue'
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiInput from '@/components/UiInput.vue'
import { useAuth } from '@/composables/useAuth'
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import $api from '@/services'
import { isApiError } from '@/services/apiClient'
import type { Invitation, JoinRequestId, UserId } from '@/services/dbTypes'
import type { GetTeamInfoResponse, ManageJoinRequestAction } from '@/services/teams/types'
import { computed, ref } from 'vue'

interface Props {
  team: GetTeamInfoResponse
  isCaptain: boolean
}

const props = defineProps<Props>()
const auth = useAuth()
const { showNotification, hideNotification } = useGlobalNotification()

const emit = defineEmits<{
  (e: 'updateTeam', newTeamValue: GetTeamInfoResponse): void
}>()

interface UserStatus {
  accepted: boolean
  declined: boolean
  invited: boolean
  pending: boolean
  source: string
}

const statusByUserId = computed<Record<UserId, UserStatus>>(() => {
  const map: Record<UserId, UserStatus> = {}

  const membersSet = new Set((props.team.members || []).map((m) => m.id))
  const myInvitationStatus = props.team.my_invitation_status
  const myJoinRequestStatus = props.team.my_join_request_status
  const invitations = props.team.invitations || []
  const joinRequests = props.team.join_requests || []

  const invitationByUserId: Record<UserId, (typeof invitations)[number]> = {}
  for (const inv of invitations) {
    const uid = inv?.user?.id
    if (uid) invitationByUserId[uid] = inv
  }

  const joinRequestByUserId: Record<UserId, (typeof joinRequests)[number]> = {}
  for (const jr of joinRequests) {
    const uid = jr?.user?.id
    if (uid) joinRequestByUserId[uid] = jr
  }

  const allUserIds = new Set<UserId>([
    ...membersSet,
    ...Object.keys(invitationByUserId).map((x) => Number(x) as UserId),
    ...Object.keys(joinRequestByUserId).map((x) => Number(x) as UserId),
  ])

  for (const userId of allUserIds) {
    const invitation = invitationByUserId[userId]
    const joinRequest = joinRequestByUserId[userId]
    const accepted = membersSet.has(userId)
    const isCurrentUser = userId === auth.user.value?.id

    const invitationStatus = invitation?.status ?? (isCurrentUser ? myInvitationStatus : null)
    const joinRequestStatus = joinRequest?.status ?? (isCurrentUser ? myJoinRequestStatus : null)

    const invited = invitationStatus === 'invited'
    const pending = joinRequestStatus === 'pending'
    const declined = invitationStatus === 'declined' || joinRequestStatus === 'declined'

    let source = 'Member'
    if (accepted) {
      if (joinRequestStatus === 'accepted') source = 'Join request'
      else if (invitationStatus === 'accepted') source = 'Invitation'
      else if (joinRequestStatus) source = 'Join request'
      else if (invitationStatus) source = 'Invitation'
    } else if (invitationStatus) source = 'Invitation'
    else if (joinRequestStatus) source = 'Join request'

    map[userId] = { accepted, declined, invited, pending, source }
  }

  return map
})

// ── search ────────────────────────────────────────────────────
const memberSearch = ref('')

const matches = (parts: (string | undefined)[]) => {
  const q = memberSearch.value.trim().toLowerCase()
  if (!q) return true
  return parts.some((p) => p?.toLowerCase().includes(q))
}

// ── members ───────────────────────────────────────────────────
const filteredMembers = computed(() =>
  props.team.members.filter((m) => matches([m.username, m.email, m.full_name])),
)

// ── join requests ─────────────────────────────────────────────
const joinRequestsLoading = ref<Record<number, boolean>>({})

const filteredPendingJoinRequests = computed(() =>
  (props.team.join_requests ?? [])
    .filter((r) => r.status === 'pending')
    .filter((r) => matches([r.user.username, r.user.email, r.user.full_name])),
)

const reviewJoinRequest = async (id: JoinRequestId, action: ManageJoinRequestAction) => {
  joinRequestsLoading.value = {
    ...joinRequestsLoading.value,
    [id]: true,
  }

  hideNotification()
  try {
    const response = await $api.teams.manageJoinRequest(id, props.team.id, action)

    emit('updateTeam', response.data)
    const pastTense = {
      accept: 'accepted',
      decline: 'declined',
    }
    showNotification(`Join request ${pastTense[action]}`, 'success')
  } catch (err) {
    if (isApiError(err)) {
      showNotification(
        err.response ? `Unavle to ${action} join request` : 'Server connection error.',
        'error',
      )
    }
  }
}

// ── invitations ───────────────────────────────────────────────
const resendInvitationsLoading = ref<Record<UserId, boolean>>({})

const uniqueInvitations = computed(() => {
  const byUserId = new Map<UserId, Invitation>()
  for (const inv of props.team.invitations) {
    const uid = inv.user.id

    const prev = byUserId.get(uid)
    if (!prev) {
      byUserId.set(uid, inv)
    }
  }
  return Array.from(byUserId.values())
})

const filteredPendingInvitations = computed(() =>
  uniqueInvitations.value
    .filter((i) => i.status === 'invited')
    .filter((i) => matches([i.user.username, i.user.email, i.user.full_name])),
)

const filteredDeclinedInvitations = computed(() =>
  uniqueInvitations.value
    .filter((i) => i.status === 'declined')
    .filter((i) => matches([i.user.username, i.user.email, i.user.full_name])),
)

const resendInvitation = async (userId: UserId) => {
  resendInvitationsLoading.value = {
    ...resendInvitationsLoading.value,
    [userId]: true,
  }

  hideNotification()
  try {
    const response = await $api.teams.resendInvatation(props.team.id, { user_id: userId })
    emit('updateTeam', response.data)
  } catch (err) {
    if (isApiError(err)) {
      showNotification(
        err.response ? 'Unable to resent invatation.' : 'Server connection error.',
        'success',
      )
    }
  }
}
</script>

<style>
.panel {
  padding: 1.2rem;
  border: 1px solid var(--line-soft);
  height: 100%;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  margin-bottom: 0.9rem;
}

.panel-head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.15rem;
}

.member-search {
  margin-bottom: 0.75rem;
}

.members-sections {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.members-section {
  display: grid;
  gap: 0.65rem;
}

.section-subhead {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.8rem;
}

.section-subhead h3 {
  margin: 0;
  font-size: 1rem;
}

.member-list {
  display: grid;
  gap: 0.55rem;
}

.invitations-list {
  grid-template-rows: auto;
}

.member-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.7rem;
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  background: #fff;
  padding: 0.65rem 0.75rem;
}

.member-name,
.member-email {
  margin: 0;
}

.member-name {
  font-weight: 700;
  color: var(--ink-900);
}

.member-email {
  font-size: 0.84rem;
}

.member-note {
  margin-top: 0.8rem;
}

.member-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.45rem;
}

.row-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

@media (max-width: 640px) {
  .member-row {
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
