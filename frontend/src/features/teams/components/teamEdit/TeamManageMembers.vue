<template>
  <ui-card class="panel members-panel">
    <header class="panel-head">
      <h2>Members management</h2>
      <span class="text-muted">{{ team.members.length }} people</span>
    </header>

    <label class="form-label member-search">
      Search members
      <ui-input v-model="memberSearch" placeholder="Search by username or email" />
    </label>

    <div class="member-list">
      <article v-for="member in filteredMembers" :key="`member-${member.id}`" class="member-row">
        <div>
          <p class="member-name">{{ member.username }}</p>
          <p class="text-muted member-email">{{ member.email }}</p>
        </div>

        <div class="member-actions">
          <ui-badge v-if="member.id === team.captain_id" variant="green">Captain</ui-badge>
          <ui-button
            v-else-if="isCaptain"
            variant="danger"
            size="sm"
            :disabled="kickLoadingByUser[member.id]"
            @click="removeMember(member)"
          >
            <loading-icon v-if="kickLoadingByUser[member.id]" />
            Remove
          </ui-button>
        </div>
      </article>
    </div>

    <div v-if="isCaptain" class="add-member-box">
      <h3>Invitations status</h3>
      <p v-if="!team.invitations?.length" class="text-muted">No invitations yet.</p>
      <div v-else class="member-list">
        <article
          v-for="invitation in team.invitations"
          :key="`inv-${invitation.id}`"
          class="member-row"
        >
          <div>
            <p class="member-name">{{ invitation.user.username }}</p>
            <p class="text-muted member-email">{{ invitation.user.email }}</p>
          </div>
          <ui-badge v-if="invitation.status === 'declined'" variant="red">
            {{ invitation.status }}
          </ui-badge>
          <ui-badge v-else>{{ invitation.status }}</ui-badge>
        </article>
      </div>
    </div>

    <p v-if="filteredMembers.length === 0" class="text-muted member-note">
      No members match your search.
    </p>

    <div v-if="isCaptain" class="add-member-box">
      <h3>Invite user</h3>

      <label class="form-label">
        Select user
        <ui-select :options="userOptions" v-model="addMemberSelection" />
      </label>

      <p v-if="availableUsers.length === 0" class="text-muted">No available users to add.</p>

      <ui-button @click="addMember" :disabled="addMemberLoading">
        {{ addMemberLoading ? 'Sending...' : 'Send invitation' }}
      </ui-button>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/UiBadge.vue'
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiInput from '@/components/UiInput.vue'
import UiSelect from '@/components/UiSelect.vue'
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import $api from '@/services'
import { isApiError } from '@/services/apiClient'
import type { User, UserId } from '@/services/dbTypes'
import type { GetTeamInfoResponse } from '@/services/teams/types'
import { computed, ref } from 'vue'

interface Props {
  isCaptain: boolean
  team: GetTeamInfoResponse
  users: Member[]
}

const props = defineProps<Props>()
const { hideNotification, showNotification } = useGlobalNotification()

const emit = defineEmits<{
  (e: 'memberDeleted'): void
  (e: 'invitedMember'): void
}>()

export type Member = Pick<User, 'id' | 'full_name' | 'email' | 'username'>

const memberSearch = ref('')
const addMemberSelection = ref('')
const addMemberLoading = ref(false)
const kickLoadingByUser = ref<Record<UserId, boolean>>({})

const availableUsers = computed(() => {
  const currentIds = new Set(props.team.members.map((member) => member.id))
  return props.users.filter((user) => !currentIds.has(user.id))
})

const filteredMembers = computed(() => {
  const search = memberSearch.value.trim().toLowerCase()
  if (!search) return props.team.members

  return props.team.members.filter((member) => {
    return [member.username, member.email, member.full_name || '']
      .join(' ')
      .toLowerCase()
      .includes(search)
  })
})

const userOptions = computed(() => [
  { value: '', label: 'Select user' },
  ...availableUsers.value.map((user) => ({
    value: String(user.id),
    label: `${user.username} (${user.email})`,
  })),
])

const removeMember = async (member: Member) => {
  if (member.id === props.team.captain_id) return
  kickLoadingByUser.value = {
    ...kickLoadingByUser.value,
    [member.id]: true,
  }
  hideNotification()

  try {
    await $api.teams.removeMember(props.team.id, member.id)

    showNotification('Member removed.', 'success')
    emit('memberDeleted')
  } catch (err) {
    if (isApiError(err)) {
      showNotification(
        err.response ? 'Uable to delete team member' : 'Server connection error.',
        'error',
      )
    }
  } finally {
    kickLoadingByUser.value = {
      ...kickLoadingByUser.value,
      [member.id]: false,
    }
  }
}

const addMember = async () => {
  if (!addMemberSelection.value) {
    showNotification('Select a user to add.', 'error')
    return
  }

  addMemberLoading.value = true
  hideNotification()

  try {
    $api.teams.addMember(props.team.id, { user_id: Number(addMemberSelection.value) })

    addMemberSelection.value = ''
    showNotification('Invitation sent.', 'success')
    emit('invitedMember')
  } catch (err) {
    if (isApiError(err)) {
      showNotification(err.response ? 'Unable to add member.' : 'Server connection error.', 'error')
    }
  } finally {
    addMemberLoading.value = false
  }
}
</script>

<style scoped>
.panel {
  border: 1px solid var(--line-soft);
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

.member-list {
  display: grid;
  gap: 0.55rem;
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

.member-actions {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.member-note {
  margin-top: 0.8rem;
}

.add-member-box {
  margin-top: 0.9rem;
  border-top: 1px solid var(--line-soft);
  padding-top: 0.9rem;
  display: grid;
  gap: 0.65rem;
}

.add-member-box h3 {
  margin: 0;
  font-size: 1rem;
}

@media (max-width: 760px) {
  .member-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
