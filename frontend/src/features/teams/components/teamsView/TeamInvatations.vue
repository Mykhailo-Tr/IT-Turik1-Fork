<template>
  <ui-card>
    <header class="section-head">
      <h2>Invitations</h2>
      <span class="text-muted">{{ pendingInboxInvitations?.length ?? 0 }} pending</span>
    </header>

    <p v-if="inboxLoading" class="text-muted">Loading invitations...</p>
    <p v-else-if="pendingInboxInvitations?.length === 0" class="text-muted">
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
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import $api from '@/services'
import { isApiError } from '@/services/apiClient'
import type { Invitation, InvitationId } from '@/services/dbTypes'
import { computed, onMounted, ref } from 'vue'

const { hideNotification, showNotification } = useGlobalNotification()
const emit = defineEmits<{
  (e: 'respondedToInvatation'): void
}>()

const inboxLoading = ref(false)
const inboxInvitations = ref<Invitation[] | null>()
const invitationActionLoading = ref<Record<InvitationId, boolean>>({})

const pendingInboxInvitations = computed(() =>
  inboxInvitations.value?.filter((invitation) => invitation.status === 'invited'),
)

const respondToInvitation = async (invitationId: InvitationId, action: 'accept' | 'decline') => {
  invitationActionLoading.value = {
    ...invitationActionLoading.value,
    [invitationId]: true,
  }
  hideNotification()

  try {
    await $api.teams.respondToInvitation(invitationId, action)

    emit('respondedToInvatation')
    showNotification(
      action === 'accept' ? 'Invitation accepted.' : 'Invitation declined.',
      'success',
    )

    await fetchInvitations()
  } catch (err) {
    if (isApiError(err)) {
      showNotification(
        err.response ? `Unable to ${action} invitation.` : 'Unable to connect to server.',
        'error',
      )
    }
  } finally {
    invitationActionLoading.value = {
      ...invitationActionLoading.value,
      [invitationId]: false,
    }
  }
}

const fetchInvitations = async () => {
  try {
    const response = await $api.teams.getInvatations()

    inboxInvitations.value = response.data
  } catch (err) {
    if (isApiError(err)) {
      showNotification(
        err.response ? 'Unable to load invitations.' : 'Unable to connect to server.',
        'error',
      )
    }
  }
}

onMounted(() => {
  fetchInvitations()
})
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
  border: 1px solid var(--line-soft);
  border-radius: 16px;
  background: #fff;
  padding: 0.95rem;
  display: grid;
  gap: 0.45rem;
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
