<template>
  <ui-card>
    <template #header>
      <div class="section-head">
        <h2>Invitations</h2>
        <ui-skeleton-loader :loading="inboxLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="70px" />
          </template>

          <span class="text-muted">{{ pendingInboxInvitations?.length ?? 0 }} pending</span>
        </ui-skeleton-loader>
      </div>
    </template>

    <ui-skeleton-loader :loading="inboxLoading">
      <template #skeleton>
        <div class="team-grid">
          <ui-card v-for="i in 2" :key="i" style="display: flex; flex-direction: column; gap: 10px">
            <template #header>
              <div class="team-meta">
                <ui-skeleton variant="rect" width="100%" />
                <ui-skeleton variant="rect" width="80px" />
              </div>
            </template>

            <ui-skeleton variant="rect" width="120px" />

            <template #footer>
              <div style="display: flex; gap: 10px">
                <ui-skeleton variant="rect" height="1.8rem" width="80px" />
                <ui-skeleton variant="rect" height="1.8rem" width="80px" />
              </div>
            </template>
          </ui-card>
        </div>
      </template>

      <p v-if="pendingInboxInvitations?.length === 0" class="text-muted">No pending invitations.</p>
      <div v-else class="team-grid">
        <ui-card
          v-for="invitation in pendingInboxInvitations"
          :key="`invite-${invitation.id}`"
          class="team-item"
        >
          <template #header>
            <div class="team-meta">
              <h3>{{ invitation.team.name }}</h3>

              <ui-badge class="text-muted">
                Invited by: {{ invitation.invited_by?.username || 'Unknown user' }}
              </ui-badge>
            </div>
          </template>

          <template #footer>
            <div class="row-actions">
              <ui-button
                size="sm"
                :disabled="loadingIds.has(invitation.id)"
                @click="respondToInvitation(invitation.id, 'accept')"
              >
                <loading-icon v-if="loadingIds.has(invitation.id)" />
                Accept
              </ui-button>
              <ui-button
                size="sm"
                variant="outline"
                :disabled="loadingIds.has(invitation.id)"
                @click="respondToInvitation(invitation.id, 'decline')"
              >
                Decline
              </ui-button>
            </div>
          </template>
        </ui-card>
      </div>
    </ui-skeleton-loader>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import { useInvitations, useRespondToInvitation } from '@/queries/teams'
import type { InvitationId } from '@/api/dbTypes'
import { computed, ref } from 'vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import UiSkeletonLoader from '@/components/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/UiSkeleton.vue'
import UiBadge from '@/components/UiBadge.vue'

const { showNotification } = useGlobalNotification()

const { data: inboxInvitations, isLoading: inboxLoading } = useInvitations()

const pendingInboxInvitations = computed(() =>
  inboxInvitations.value?.filter((invitation) => invitation.status === 'invited'),
)

const { mutate: respond } = useRespondToInvitation()
const loadingIds = ref<Set<InvitationId>>(new Set())

const respondToInvitation = (invitationId: InvitationId, action: 'accept' | 'decline') => {
  loadingIds.value.add(invitationId)
  respond(
    { id: invitationId, action },
    {
      onSuccess: () => {
        showNotification(
          action === 'accept' ? 'Invitation accepted.' : 'Invitation declined.',
          'success',
        )
      },
      onError: (err) => {
        showNotification(
          err.response ? `Unable to ${action} invitation.` : 'Unable to connect to server.',
          'error',
        )
      },
      onSettled: () => {
        loadingIds.value.delete(invitationId)
      },
    },
  )
}
</script>

<style>
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  margin-bottom: 0.8rem;
}

.section-head h2 {
  margin: 0;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.9rem;
}

.team-item {
  padding: 0.95rem;
}

.team-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.team-meta h3 {
  margin: 0;
  font-family: var(--font-display);
}

.team-item p {
  margin: 0;
}

.row-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

@media (max-width: 640px) {
  .section-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
