<template>
  <section class="page-shell teams-detail-page">
    <article class="card hero-card">
      <p class="section-eyebrow">Team workspace</p>
      <h1 class="section-title">{{ team?.name || 'Team details' }}</h1>
      <p class="section-subtitle">Manage team information and members in one place.</p>
      <div class="hero-actions">
        <router-link to="/teams" class="btn-soft action-link">Back to teams</router-link>
        <router-link v-if="team && isCaptain" :to="`/teams/${team.id}/edit`" class="btn-primary action-link">
          Edit team
        </router-link>
        <button v-if="team && isCaptain" class="btn-danger" type="button" @click="openDeleteModal(team)">
          Delete team
        </button>
      </div>
    </article>

    <div v-if="notification" :class="['notice', notification.type]">{{ notification.message }}</div>

    <div v-if="loading" class="card state-card text-muted">Loading team workspace...</div>
    <div v-else-if="loadError" class="card state-card text-error">{{ loadError }}</div>

    <template v-else-if="team">
      <div class="workspace-grid">
        <div class="left-column">
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
            </div>
          </article>

          <article class="card panel contacts-panel">
            <header class="panel-head">
              <h2>Contacts</h2>
            </header>
            <div class="contacts-list">
              <p>
                <strong>Telegram:</strong>
                <a v-if="team.contact_telegram" :href="telegramLink(team.contact_telegram)" target="_blank" rel="noopener noreferrer">
                  @{{ team.contact_telegram }}
                </a>
                <span v-else>-</span>
              </p>
              <p>
                <strong>Discord:</strong>
                <a v-if="team.contact_discord" :href="discordLink(team.contact_discord)" target="_blank" rel="noopener noreferrer">
                  {{ team.contact_discord }}
                </a>
                <span v-else>-</span>
              </p>
            </div>
          </article>
        </div>

        <article class="card panel members-panel">
          <header class="panel-head">
            <h2>Members</h2>
            <span class="text-muted">{{ team.members.length }} people</span>
          </header>

          <div class="member-list">
            <article
              v-for="member in team.members"
              :key="`team-${team.id}-member-${member.id}`"
              class="member-row"
            >
              <div>
                <p class="member-name">{{ member.username }}</p>
                <p class="text-muted member-email">{{ member.email }}</p>
              </div>

              <div class="member-actions">
                <span v-if="member.id === team.captain_id" class="captain-tag">Captain</span>
                <button
                  v-else-if="isCaptain"
                  type="button"
                  class="btn-danger btn-small"
                  @click="openKickModal(team, member)"
                >
                  Remove
                </button>
              </div>
            </article>
          </div>

          <div v-if="isCaptain" class="manage-box">
            <h3>Manage members</h3>
            <label class="form-label">
              Search users
              <input
                v-model="memberSearch"
                class="input-control"
                type="text"
                placeholder="Search by username, email, full name"
              />
            </label>

            <label class="form-label">
              Add member
              <select v-model="addMemberSelection" class="select-control">
                <option value="">Select user</option>
                <option v-for="user in availableUsers" :key="`add-${user.id}`" :value="String(user.id)">
                  {{ user.username }} ({{ user.email }})
                </option>
              </select>
            </label>

            <button class="btn-primary" type="button" @click="addMember" :disabled="addMemberLoading">
              {{ addMemberLoading ? 'Adding...' : 'Add member' }}
            </button>
          </div>
          <p v-else class="text-muted member-note">Only team captain can manage members.</p>
        </article>
      </div>
    </template>

    <div v-if="isDeleteModalOpen" class="modal-backdrop" @click.self="closeDeleteModal">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="delete-team-title">
        <h3 id="delete-team-title">Delete team</h3>
        <p class="modal-text">
          Are you sure you want to permanently delete
          <strong>{{ teamPendingDelete?.name }}</strong>?
        </p>

        <p v-if="deleteError" class="text-error modal-error">{{ deleteError }}</p>

        <div class="modal-actions">
          <button class="btn-cancel" type="button" :disabled="deleteTeamLoading" @click="closeDeleteModal">Cancel</button>
          <button class="btn-danger" type="button" :disabled="deleteTeamLoading" @click="confirmDeleteTeam">
            {{ deleteTeamLoading ? 'Deleting...' : 'Delete permanently' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="isKickModalOpen" class="modal-backdrop" @click.self="closeKickModal">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="kick-member-title">
        <h3 id="kick-member-title">Remove member</h3>
        <p class="modal-text">
          Remove
          <strong>{{ memberPendingKick?.username }}</strong>
          from
          <strong>{{ memberPendingKick?.teamName }}</strong>
          ?
        </p>

        <p v-if="kickError" class="text-error modal-error">{{ kickError }}</p>

        <div class="modal-actions">
          <button class="btn-cancel" type="button" :disabled="kickLoading" @click="closeKickModal">Cancel</button>
          <button class="btn-danger" type="button" :disabled="kickLoading" @click="confirmKickMember">
            {{ kickLoading ? 'Removing...' : 'Remove member' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { API_BASE } from '@/features/shared/config/api'

const route = useRoute()
const router = useRouter()

const team = ref(null)
const users = ref([])
const currentUserId = ref(null)

const loading = ref(true)
const loadError = ref('')
const notification = ref(null)

const memberSearch = ref('')
const addMemberSelection = ref('')
const addMemberLoading = ref(false)

const isDeleteModalOpen = ref(false)
const deleteTeamLoading = ref(false)
const deleteError = ref('')
const teamPendingDelete = ref(null)

const isKickModalOpen = ref(false)
const kickLoading = ref(false)
const kickError = ref('')
const memberPendingKick = ref(null)

const teamId = computed(() => Number(route.params.id))
const isCaptain = computed(() => Boolean(team.value) && team.value.captain_id === currentUserId.value)

const captainName = computed(() => {
  if (!team.value) return '-'
  const captain = team.value.members.find((member) => member.id === team.value.captain_id)
  return captain?.username || `User #${team.value.captain_id}`
})

const availableUsers = computed(() => {
  if (!isCaptain.value || !team.value) return []

  const currentIds = new Set(team.value.members.map((member) => member.id))
  const search = memberSearch.value.trim().toLowerCase()

  return users.value.filter((user) => {
    if (currentIds.has(user.id)) return false
    if (!search) return true
    return [user.username, user.email, user.full_name || ''].join(' ').toLowerCase().includes(search)
  })
})

const authHeaders = (json = false) => {
  const token = localStorage.getItem('access')
  const headers = { Authorization: `Bearer ${token}` }
  if (json) headers['Content-Type'] = 'application/json'
  return headers
}

const logoutToLogin = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  localStorage.removeItem('needs_onboarding')
  router.push('/login')
}

const telegramLink = (username) => `https://t.me/${String(username || '').replace(/^@/, '')}`
const discordLink = (username) => `https://discord.com/users/@${encodeURIComponent(String(username || '').replace(/^@/, ''))}`

const parseApiError = async (response, fallbackMessage) => {
  try {
    const data = await response.json()
    if (typeof data === 'string') return data
    if (data.detail) return data.detail
    return JSON.stringify(data)
  } catch {
    return fallbackMessage
  }
}

const fetchProfile = async () => {
  const response = await fetch(`${API_BASE}/api/accounts/profile/`, {
    headers: authHeaders(false),
  })

  if (response.status === 401) {
    logoutToLogin()
    return false
  }

  if (!response.ok) {
    loadError.value = 'Unable to load profile information.'
    return false
  }

  const data = await response.json()
  currentUserId.value = data.id

  if (data.needs_onboarding) {
    localStorage.setItem('needs_onboarding', '1')
    router.push('/complete-profile')
    return false
  }

  return true
}

const fetchTeam = async () => {
  if (!teamId.value) {
    loadError.value = 'Invalid team id.'
    return false
  }

  const response = await fetch(`${API_BASE}/api/accounts/teams/${teamId.value}/`, {
    headers: authHeaders(false),
  })

  if (response.status === 401) {
    logoutToLogin()
    return false
  }

  if (response.status === 404) {
    loadError.value = 'Team not found.'
    team.value = null
    return false
  }

  if (!response.ok) {
    loadError.value = await parseApiError(response, 'Unable to load team information.')
    team.value = null
    return false
  }

  team.value = await response.json()
  return true
}

const fetchUsers = async () => {
  const response = await fetch(`${API_BASE}/api/accounts/users/`, {
    headers: authHeaders(false),
  })

  if (response.status === 401) {
    logoutToLogin()
    return false
  }

  if (!response.ok) {
    notification.value = { type: 'error', message: 'Unable to load users list.' }
    return false
  }

  users.value = await response.json()
  return true
}

const loadWorkspace = async () => {
  loading.value = true
  loadError.value = ''

  const profileOk = await fetchProfile()
  if (!profileOk) {
    loading.value = false
    return
  }

  const teamOk = await fetchTeam()
  if (teamOk && isCaptain.value) {
    await fetchUsers()
  }

  loading.value = false
}

const addMember = async () => {
  if (!team.value || !isCaptain.value) return
  if (!addMemberSelection.value) {
    notification.value = { type: 'error', message: 'Select a user to add.' }
    return
  }

  addMemberLoading.value = true
  notification.value = null
  try {
    const response = await fetch(`${API_BASE}/api/accounts/teams/${team.value.id}/members/`, {
      method: 'POST',
      headers: authHeaders(true),
      body: JSON.stringify({ user_id: Number(addMemberSelection.value) }),
    })

    if (response.status === 401) {
      logoutToLogin()
      return
    }

    if (!response.ok) {
      notification.value = { type: 'error', message: await parseApiError(response, 'Unable to add member.') }
      return
    }

    addMemberSelection.value = ''
    memberSearch.value = ''
    notification.value = { type: 'success', message: 'Member added.' }
    await Promise.all([fetchTeam(), fetchUsers()])
  } catch {
    notification.value = { type: 'error', message: 'Server connection error.' }
  } finally {
    addMemberLoading.value = false
  }
}

const openKickModal = (sourceTeam, member) => {
  memberPendingKick.value = {
    teamId: sourceTeam.id,
    teamName: sourceTeam.name,
    userId: member.id,
    username: member.username,
  }
  kickError.value = ''
  isKickModalOpen.value = true
}

const closeKickModal = (force = false) => {
  if (kickLoading.value && !force) return
  isKickModalOpen.value = false
  memberPendingKick.value = null
}

const confirmKickMember = async () => {
  if (!memberPendingKick.value || !team.value) return

  kickLoading.value = true
  kickError.value = ''
  notification.value = null

  try {
    const response = await fetch(
      `${API_BASE}/api/accounts/teams/${memberPendingKick.value.teamId}/members/${memberPendingKick.value.userId}/`,
      { method: 'DELETE', headers: authHeaders(false) },
    )

    if (response.status === 401) {
      logoutToLogin()
      return
    }

    if (!response.ok && response.status !== 204) {
      kickError.value = await parseApiError(response, 'Unable to remove member.')
      return
    }

    notification.value = { type: 'success', message: 'Member removed.' }
    closeKickModal(true)
    await Promise.all([fetchTeam(), fetchUsers()])
  } catch {
    kickError.value = 'Server connection error.'
  } finally {
    kickLoading.value = false
  }
}

const openDeleteModal = (sourceTeam) => {
  teamPendingDelete.value = sourceTeam
  deleteError.value = ''
  isDeleteModalOpen.value = true
}

const closeDeleteModal = (force = false) => {
  if (deleteTeamLoading.value && !force) return
  isDeleteModalOpen.value = false
  teamPendingDelete.value = null
}

const confirmDeleteTeam = async () => {
  if (!teamPendingDelete.value) return

  deleteTeamLoading.value = true
  deleteError.value = ''
  notification.value = null

  try {
    const response = await fetch(`${API_BASE}/api/accounts/teams/${teamPendingDelete.value.id}/`, {
      method: 'DELETE',
      headers: authHeaders(false),
    })

    if (response.status === 401) {
      logoutToLogin()
      return
    }

    if (!response.ok && response.status !== 204) {
      deleteError.value = await parseApiError(response, 'Unable to delete team.')
      return
    }

    closeDeleteModal(true)
    router.push('/teams')
  } catch {
    deleteError.value = 'Server connection error.'
  } finally {
    deleteTeamLoading.value = false
  }
}

onMounted(loadWorkspace)

watch(
  () => route.params.id,
  () => {
    loadWorkspace()
  },
)
</script>

<style scoped>
.teams-detail-page {
  gap: 1.2rem;
}

.hero-card,
.state-card,
.panel {
  padding: 1.2rem;
}

.hero-card {
  background:
    linear-gradient(135deg, rgba(13, 148, 136, 0.14), rgba(15, 23, 42, 0.03)),
    #fff;
  border: 1px solid rgba(13, 148, 136, 0.22);
}

.hero-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.action-link {
  text-decoration: none;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 1rem;
  align-items: start;
}

.left-column {
  display: grid;
  gap: 1rem;
}

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

.status-badge {
  border-radius: 999px;
  border: 1px solid rgba(20, 184, 166, 0.45);
  background: rgba(20, 184, 166, 0.15);
  color: var(--brand-700);
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
}

.info-item {
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  padding: 0.7rem;
  background: rgba(255, 255, 255, 0.9);
}

.info-item span {
  display: block;
  color: var(--ink-500);
  font-size: 0.8rem;
}

.info-item strong {
  color: var(--ink-900);
}

.contacts-list {
  display: grid;
  gap: 0.5rem;
}

.contacts-list p {
  margin: 0;
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

.captain-tag {
  border-radius: 999px;
  border: 1px solid rgba(14, 116, 144, 0.35);
  background: rgba(14, 116, 144, 0.14);
  color: #0e7490;
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
}

.manage-box {
  margin-top: 0.9rem;
  border-top: 1px solid var(--line-soft);
  padding-top: 0.9rem;
  display: grid;
  gap: 0.65rem;
}

.manage-box h3 {
  margin: 0;
  font-size: 1rem;
}

.member-note {
  margin-top: 0.9rem;
}

.btn-soft {
  border: 1px solid var(--line-strong);
  background: #fff;
  border-radius: 10px;
  padding: 0.45rem 0.7rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.btn-danger {
  border: 1px solid #dc2626;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 10px;
  padding: 0.45rem 0.7rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.btn-small {
  padding: 0.28rem 0.55rem;
  font-size: 0.8rem;
}

.btn-cancel {
  border: 1px solid var(--line-strong);
  background: #fff;
  border-radius: 10px;
  padding: 0.45rem 0.7rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: grid;
  place-items: center;
  z-index: 50;
  padding: 1rem;
}

.modal-card {
  width: min(100%, 500px);
  background: #fff;
  border-radius: 16px;
  border: 1px solid var(--line-soft);
  box-shadow: var(--shadow-lg);
  padding: 1.2rem;
}

.modal-card h3 {
  margin: 0;
  font-family: var(--font-display);
}

.modal-text {
  margin: 0.7rem 0;
  color: var(--ink-700);
}

.modal-error {
  margin: 0.5rem 0 0;
}

.modal-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
}

@media (max-width: 1020px) {
  .workspace-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .info-grid {
    grid-template-columns: 1fr;
  }

  .member-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
