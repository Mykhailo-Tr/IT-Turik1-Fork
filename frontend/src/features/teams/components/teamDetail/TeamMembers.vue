<template>
  <ui-card class="panel members-panel" :is-error="loadingError">
    <template #error>
      <div style="display: flex; justify-content: center; align-items: center; height: 502px">
        <p>Failed to fetch members</p>
      </div>
    </template>

    <header class="panel-head">
      <h2>Members</h2>

      <ui-skeleton-loader :loading="props.loading">
        <template #skeleton>
          <ui-skeleton variant="rect" width="80px" />
        </template>

        <span class="text-muted">{{ props.team?.members.length ?? 0 }} accepted</span>
      </ui-skeleton-loader>
    </header>

    <div class="form-item">
      <ui-input
        v-model="memberSearch"
        placeholder="Search by username or email"
        :disabled="props.loading"
      />
    </div>

    <div class="members-sections">
      <section class="members-section">
        <header class="section-subhead">
          <h3>Members</h3>
          <ui-skeleton-loader :loading="props.loading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="80px" />
            </template>

            <span class="text-muted">{{ filteredMembers?.length }} people</span>
          </ui-skeleton-loader>
        </header>

        <ui-skeleton-loader :loading="props.loading">
          <template #skeleton>
            <div class="member-list">
              <ui-card
                v-for="i in 2"
                :key="i"
                style="display: flex; flex-direction: column; gap: 10px"
              >
                <template #header>
                  <div style="display: flex; justify-content: space-between; gap: 10px">
                    <ui-skeleton variant="rect" width="100%" />
                    <ui-skeleton variant="rect" width="100px" />
                  </div>
                </template>

                <ui-skeleton variant="rect" width="200px" />
              </ui-card>
            </div>
          </template>

          <div class="member-list">
            <ui-card v-for="member in filteredMembers" :key="`member-${member.id}`">
              <template #header>
                <div style="display: flex; justify-content: space-between">
                  <p class="member-name">{{ member.username }}</p>

                  <ui-badge v-if="member.id === props.team?.captain_id" variant="green"
                    >Captain</ui-badge
                  >
                </div>
              </template>
              <p class="text-muted member-email">{{ member.email }}</p>

              <div class="member-side">
                <template>
                  <ui-badge variant="gray">{{
                    statusByUserId[member.id]?.source || 'Member'
                  }}</ui-badge>
                </template>
              </div>
            </ui-card>

            <p v-if="filteredMembers?.length === 0" class="text-muted">
              No accepted members match your search.
            </p>
          </div>
        </ui-skeleton-loader>
      </section>

      <section>
        <ui-skeleton-loader :loading="props.loading">
          <template #skeleton>
            <div class="members-section">
              <header class="section-subhead">
                <ui-skeleton variant="rect" width="150px" />
                <ui-skeleton variant="rect" width="50px" />
              </header>

              <div class="member-list">
                <ui-card v-for="i in 2" :key="i">
                  <div style="display: flex; flex-direction: column; gap: 5px">
                    <ui-skeleton variant="rect" width="200px" />
                    <ui-skeleton variant="rect" width="200px" />
                  </div>

                  <template #footer>
                    <div class="row-actions">
                      <ui-skeleton variant="rect" width="80px" />
                      <ui-skeleton variant="rect" width="80px" />
                    </div>
                  </template>
                </ui-card>
              </div>
            </div>
          </template>

          <div v-if="props.isCaptain" class="join-request-list">
            <header class="section-subhead">
              <h3>Join Requests</h3>
              <span class="text-muted">{{ filteredPendingJoinRequests?.length }} pending</span>
            </header>

            <ui-card
              v-for="joinRequest in filteredPendingJoinRequests"
              :key="`join-request-${joinRequest.id}`"
            >
              <div>
                <p class="member-name">{{ joinRequest.user.username }}</p>
                <p class="text-muted member-email">{{ joinRequest.user.email }}</p>
              </div>

              <template #footer>
                <div>
                  <ui-badge v-if="joinRequest.user.id === props.team?.captain_id" variant="green"
                    >Captain</ui-badge
                  >
                  <template v-else>
                    <div class="row-actions">
                      <ui-button
                        size="sm"
                        :disabled="loadingJoinRequestIds.has(joinRequest.id)"
                        @click="reviewJoinRequest(joinRequest.id, 'accept')"
                      >
                        <loading-icon v-if="loadingJoinRequestIds.has(joinRequest.id)" />
                        Accept
                      </ui-button>
                      <ui-button
                        variant="outline"
                        size="sm"
                        :disabled="loadingJoinRequestIds.has(joinRequest.id)"
                        @click="reviewJoinRequest(joinRequest.id, 'decline')"
                      >
                        Decline
                      </ui-button>
                    </div>
                  </template>
                </div>
              </template>
            </ui-card>

            <p v-if="filteredPendingJoinRequests?.length === 0" class="text-muted">
              No pending join requests.
            </p>
          </div>
        </ui-skeleton-loader>
      </section>

      <ui-skeleton-loader :loading="props.loading">
        <section v-if="props.isCaptain" class="invitations-list">
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
            v-if="
              filteredPendingInvitations.length === 0 && filteredDeclinedInvitations.length === 0
            "
            class="text-muted"
          >
            No invitations yet.
          </p>

          <div v-else class="invitations-list">
            <ui-card
              v-for="invitation in filteredPendingInvitations"
              :key="`invitation-pending-${invitation.id}`"
            >
              <template #header>
                <div style="display: flex; justify-content: space-between">
                  <p class="member-name">{{ invitation.user.username }}</p>
                  <ui-badge class>invited</ui-badge>
                </div>
              </template>

              <p class="text-muted member-email">{{ invitation.user.email }}</p>

              <div class="member-side">
                <ui-badge v-if="invitation.user.id === props.team?.captain_id" variant="green"
                  >Captain</ui-badge
                >
                <template v-else> </template>
              </div>
            </ui-card>

            <ui-card
              v-for="invitation in filteredDeclinedInvitations"
              :key="`invitation-declined-${invitation.id}`"
            >
              <template #header>
                <div style="display: flex; justify-content: space-between">
                  <p class="member-name">{{ invitation.user.username }}</p>
                  <ui-badge v-if="invitation.user.id === props.team?.captain_id" variant="green"
                    >Captain</ui-badge
                  >
                  <div v-else style="display: flex; gap: 4px">
                    <ui-badge variant="red">Declined</ui-badge>
                    <ui-badge>Invatation</ui-badge>
                  </div>
                </div>
              </template>

              <p class="text-muted member-email">{{ invitation.user.email }}</p>

              <template #footer>
                <div class="row-actions">
                  <ui-button
                    variant="outline"
                    size="sm"
                    :disabled="loadingInvitationIds.has(invitation.id)"
                    @click="resendInvitation(invitation.user.id)"
                  >
                    <loading-icon v-if="loadingInvitationIds.has(invitation.id)" />
                    Resend invitation
                  </ui-button>
                </div>
              </template>
            </ui-card>
          </div>
        </section>
      </ui-skeleton-loader>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/UiBadge.vue'
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiInput from '@/components/UiInput.vue'
import { useNotification } from '@/composables/useNotification'
import type { Invitation, JoinRequest, JoinRequestId, UserId } from '@/api/dbTypes'
import type { GetTeamInfoResponse, ManageJoinRequestAction } from '@/api/teams/types'
import { computed, ref } from 'vue'
import { useManageJoinRequest, useResendInvitation } from '@/queries/teams'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import UiSkeletonLoader from '@/components/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/UiSkeleton.vue'
import type { GetProfileResponse } from '@/api/accounts/types'

interface Props {
  team?: GetTeamInfoResponse
  user?: GetProfileResponse
  loading: boolean
  loadingError?: boolean
  isCaptain: boolean
}

const props = defineProps<Props>()
const { showNotification, hideNotification } = useNotification()

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

  const membersSet = new Set((props.team?.members || []).map((m) => m.id))
  const myInvitationStatus = props.team?.my_invitation_status
  const myJoinRequestStatus = props.team?.my_join_request_status
  const invitations = props.team?.invitations || []
  const joinRequests = props.team?.join_requests || []

  const invitationByUserId: Record<UserId, Invitation> = {}
  for (const inv of invitations) {
    const uid = inv?.user?.id
    if (uid) invitationByUserId[uid] = inv
  }

  const joinRequestByUserId: Record<UserId, JoinRequest> = {}
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
    const isCurrentUser = userId === props.user?.id

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
  props.team?.members.filter((m) => matches([m.username, m.email, m.full_name])),
)

// ── join requests ─────────────────────────────────────────────
const filteredPendingJoinRequests = computed(() =>
  props.team?.join_requests
    ?.filter((r) => r.status === 'pending')
    .filter((r) => matches([r.user.username, r.user.email, r.user.full_name])),
)

const loadingJoinRequestIds = ref<Set<JoinRequestId>>(new Set())
const { mutate: manageJoinRequestMutate } = useManageJoinRequest()

const reviewJoinRequest = (id: JoinRequestId, action: ManageJoinRequestAction) => {
  if (!props.team) return

  loadingJoinRequestIds.value.add(id)
  hideNotification()

  manageJoinRequestMutate(
    { id, teamId: props.team?.id, action },
    {
      onSuccess: () => {
        const pastTense = { accept: 'accepted', decline: 'declined' }
        showNotification(`Join request ${pastTense[action]}`, 'success')
      },
      onError: (err) => {
        showNotification(
          err.response ? `Unable to ${action} join request` : 'Server connection error.',
          'error',
        )
      },
      onSettled: () => {
        loadingJoinRequestIds.value.delete(id)
      },
    },
  )
}

// ── invitations ───────────────────────────────────────────────
const uniqueInvitations = computed(() => {
  const byUserId = new Map<UserId, Invitation>()
  for (const inv of props.team?.invitations ?? []) {
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

const loadingInvitationIds = ref<Set<UserId>>(new Set())
const { mutate: resendInvitationMutate } = useResendInvitation()

const resendInvitation = (userId: UserId) => {
  if (!props.team) return

  loadingInvitationIds.value.add(userId)
  hideNotification()

  resendInvitationMutate(
    { teamId: props.team.id, body: { user_id: userId } },
    {
      onSuccess: (data) => {
        emit('updateTeam', data)
      },
      onError: (err) => {
        showNotification(
          err.response ? 'Unable to resend invitation.' : 'Server connection error.',
          'error',
        )
      },
      onSettled: () => {
        loadingInvitationIds.value.delete(userId)
      },
    },
  )
}
</script>

<style scoped>
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

.form-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 12px;
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

.member-list,
.invitations-list,
.join-request-list {
  overflow-y: auto;
  max-height: 300px;
  display: grid;
  gap: 0.55rem;
  grid-template-rows: auto;
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
  .member-side {
    align-items: flex-start;
  }

  .status-tags {
    justify-content: flex-start;
  }
}
</style>
