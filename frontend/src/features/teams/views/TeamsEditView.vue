<template>
  <section class="page-shell teams-page">
    <article class="card header-card">
      <p class="section-eyebrow">Teams</p>
      <h1 class="section-title">Edit teams</h1>
      <p class="section-subtitle">Manage existing teams where you are the captain.</p>
      <router-link to="/teams" class="back-link">Back to teams list</router-link>
    </article>

    <article class="card teams-card">
      <h2>My captain teams</h2>
      <p v-if="notification" :class="['notice', notification.type]">{{ notification.message }}</p>
      <p v-if="loading" class="text-muted">Loading teams...</p>
      <p v-else-if="captainTeams.length === 0" class="text-muted">You are not a captain of any team yet.</p>

      <div v-else class="team-grid">
        <article
          v-for="team in captainTeams"
          :id="`team-edit-${team.id}`"
          :key="team.id"
          :class="['team-item', { focused: focusedTeamId === team.id }]"
        >
          <header class="team-head">
            <div>
              <h3>{{ team.name }}</h3>
              <p class="text-muted">Captain: {{ captainName(team) }}</p>
            </div>

            <div class="team-actions">
              <button class="btn-soft" type="button" @click="toggleEdit(team)">
                {{ isEditing(team.id) ? 'Cancel edit' : 'Edit' }}
              </button>
              <button class="btn-danger" type="button" @click="openDeleteModal(team)">Delete</button>
            </div>
          </header>

          <p><strong>Email:</strong> {{ team.email }}</p>
          <p><strong>Organization:</strong> {{ team.organization || '-' }}</p>
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

          <div class="members-box">
            <p><strong>Members:</strong></p>
            <div class="member-chips">
              <span v-for="member in team.members" :key="`team-${team.id}-member-${member.id}`" class="chip">
                {{ member.username }}
                <button
                  v-if="member.id !== team.captain_id"
                  type="button"
                  class="chip-remove"
                  @click="openKickModal(team, member)"
                >
                  x
                </button>
              </span>
            </div>
          </div>

          <div class="manage-box">
            <label class="form-label">
              Add member
              <select v-model="addMemberSelection[team.id]" class="select-control">
                <option value="">Select user</option>
                <option v-for="user in availableUsersForTeam(team)" :key="`add-${team.id}-${user.id}`" :value="String(user.id)">
                  {{ user.username }} ({{ user.email }})
                </option>
              </select>
            </label>
            <button class="btn-soft" type="button" @click="addMember(team)">Add member</button>
          </div>

          <form v-if="isEditing(team.id)" class="edit-grid" @submit.prevent="saveTeam(team.id)">
            <label class="form-label">
              Name
              <input v-model="editForms[team.id].name" class="input-control" type="text" required />
            </label>
            <label class="form-label">
              Email
              <input v-model="editForms[team.id].email" class="input-control" type="email" required />
            </label>
            <label class="form-label">
              Organization
              <input v-model="editForms[team.id].organization" class="input-control" type="text" />
            </label>
            <label class="form-label">
              Telegram
              <input
                v-model="editForms[team.id].contact_telegram"
                class="input-control"
                type="text"
                pattern="^@?[A-Za-z][A-Za-z0-9_]{4,31}$"
                title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
              />
            </label>
            <label class="form-label">
              Discord
              <input
                v-model="editForms[team.id].contact_discord"
                class="input-control"
                type="text"
                pattern="^@?(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?$"
                title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
              />
            </label>
            <button class="btn-primary" type="submit">Save changes</button>
          </form>
        </article>
      </div>
    </article>

    <div v-if="isDeleteModalOpen" class="modal-backdrop" @click.self="closeDeleteModal">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="delete-team-title">
        <h3 id="delete-team-title">Delete team</h3>
        <p class="modal-text">
          Are you sure you want to permanently delete
          <strong>{{ teamPendingDelete?.name }}</strong>?
        </p>

        <p v-if="deleteError" class="text-error modal-error">{{ deleteError }}</p>

        <div class="modal-actions">
          <button class="btn-cancel" type="button" :disabled="deleteTeamLoading" @click="closeDeleteModal">
            Cancel
          </button>
          <button class="btn-danger" type="button" :disabled="deleteTeamLoading" @click="confirmDeleteTeam">
            {{ deleteTeamLoading ? 'Deleting...' : 'Delete permanently' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="isKickModalOpen" class="modal-backdrop" @click.self="closeKickModal">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="kick-member-title">
        <h3 id="kick-member-title">Remove team member</h3>
        <p class="modal-text">
          Remove
          <strong>{{ memberPendingKick?.username }}</strong>
          from
          <strong>{{ memberPendingKick?.teamName }}</strong>
          ?
        </p>

        <p v-if="kickError" class="text-error modal-error">{{ kickError }}</p>

        <div class="modal-actions">
          <button class="btn-cancel" type="button" :disabled="kickLoading" @click="closeKickModal">
            Cancel
          </button>
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

const router = useRouter()
const route = useRoute()

const teams = ref([])
const users = ref([])
const loading = ref(true)
const notification = ref(null)
const currentUserId = ref(null)

const addMemberSelection = ref({})
const editState = ref({})
const editForms = ref({})
const isDeleteModalOpen = ref(false)
const deleteTeamLoading = ref(false)
const deleteError = ref('')
const teamPendingDelete = ref(null)
const isKickModalOpen = ref(false)
const kickLoading = ref(false)
const kickError = ref('')
const memberPendingKick = ref(null)
const focusedTeamId = ref(null)

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

const captainName = (team) => {
  const captain = team.members.find((member) => member.id === team.captain_id)
  return captain?.username || `User #${team.captain_id}`
}

const captainTeams = computed(() => teams.value.filter((team) => team.captain_id === currentUserId.value))
const isEditing = (teamId) => Boolean(editState.value[teamId])

const availableUsersForTeam = (team) => {
  const currentIds = new Set(team.members.map((member) => member.id))
  return users.value.filter((user) => !currentIds.has(user.id))
}

const telegramLink = (username) => `https://t.me/${String(username || '').replace(/^@/, '')}`
const discordLink = (username) => `https://discord.com/users/@${encodeURIComponent(String(username || '').replace(/^@/, ''))}`

const fetchProfile = async () => {
  const response = await fetch(`${API_BASE}/api/accounts/profile/`, {
    headers: authHeaders(false),
  })
  if (response.status === 401) {
    logoutToLogin()
    return false
  }
  if (!response.ok) {
    notification.value = { type: 'error', message: 'Unable to load profile information.' }
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

const fetchTeams = async () => {
  const response = await fetch(`${API_BASE}/api/accounts/teams/`, {
    headers: authHeaders(false),
  })
  if (response.status === 401) {
    logoutToLogin()
    return
  }
  if (!response.ok) {
    notification.value = { type: 'error', message: 'Unable to load teams.' }
    return
  }
  teams.value = await response.json()
}

const fetchUsers = async () => {
  const response = await fetch(`${API_BASE}/api/accounts/users/`, {
    headers: authHeaders(false),
  })
  if (response.status === 401) {
    logoutToLogin()
    return
  }
  if (!response.ok) {
    notification.value = { type: 'error', message: 'Unable to load users list.' }
    return
  }
  users.value = await response.json()
}

const toggleEdit = (team) => {
  if (isEditing(team.id)) {
    editState.value[team.id] = false
    return
  }

  editState.value[team.id] = true
  editForms.value[team.id] = {
    name: team.name,
    email: team.email,
    organization: team.organization || '',
    contact_telegram: team.contact_telegram || '',
    contact_discord: team.contact_discord || '',
  }
}

const focusTeamCard = (teamId) => {
  focusedTeamId.value = teamId
  requestAnimationFrame(() => {
    const el = document.getElementById(`team-edit-${teamId}`)
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  })
}

const openTeamFromQuery = (teamParam) => {
  const teamId = Number(teamParam)
  if (!teamId) {
    focusedTeamId.value = null
    return
  }
  const team = captainTeams.value.find((item) => item.id === teamId)
  if (!team) return
  if (!isEditing(teamId)) toggleEdit(team)
  focusTeamCard(teamId)
}

const saveTeam = async (teamId) => {
  const payload = editForms.value[teamId]
  if (!payload) return

  notification.value = null
  try {
    const response = await fetch(`${API_BASE}/api/accounts/teams/${teamId}/`, {
      method: 'PATCH',
      headers: authHeaders(true),
      body: JSON.stringify(payload),
    })

    if (response.status === 401) {
      logoutToLogin()
      return
    }
    if (!response.ok) {
      const errorData = await response.json()
      notification.value = { type: 'error', message: JSON.stringify(errorData) }
      return
    }

    notification.value = { type: 'success', message: 'Team updated successfully.' }
    editState.value[teamId] = false
    await fetchTeams()
  } catch {
    notification.value = { type: 'error', message: 'Server connection error.' }
  }
}

const addMember = async (team) => {
  const selectedUserId = addMemberSelection.value[team.id]
  if (!selectedUserId) {
    notification.value = { type: 'error', message: 'Select a user to add.' }
    return
  }

  notification.value = null
  try {
    const response = await fetch(`${API_BASE}/api/accounts/teams/${team.id}/members/`, {
      method: 'POST',
      headers: authHeaders(true),
      body: JSON.stringify({ user_id: Number(selectedUserId) }),
    })

    if (response.status === 401) {
      logoutToLogin()
      return
    }
    if (!response.ok) {
      const errorData = await response.json()
      notification.value = { type: 'error', message: JSON.stringify(errorData) }
      return
    }

    addMemberSelection.value[team.id] = ''
    notification.value = { type: 'success', message: 'Member added.' }
    await fetchTeams()
  } catch {
    notification.value = { type: 'error', message: 'Server connection error.' }
  }
}

const openKickModal = (team, member) => {
  memberPendingKick.value = {
    teamId: team.id,
    teamName: team.name,
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
  if (!memberPendingKick.value) return

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
      const errorData = await response.json()
      kickError.value = JSON.stringify(errorData)
      return
    }

    notification.value = { type: 'success', message: 'Member removed.' }
    closeKickModal(true)
    await fetchTeams()
  } catch {
    kickError.value = 'Server connection error.'
  } finally {
    kickLoading.value = false
  }
}

const openDeleteModal = (team) => {
  teamPendingDelete.value = team
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
      const errorData = await response.json()
      deleteError.value = JSON.stringify(errorData)
      return
    }

    notification.value = { type: 'success', message: 'Team deleted.' }
    closeDeleteModal(true)
    await fetchTeams()
  } catch {
    deleteError.value = 'Server connection error.'
  } finally {
    deleteTeamLoading.value = false
  }
}

onMounted(async () => {
  const ok = await fetchProfile()
  if (!ok) {
    loading.value = false
    return
  }

  await Promise.all([fetchTeams(), fetchUsers()])
  openTeamFromQuery(route.query.team)
  loading.value = false
})

watch(
  () => route.query.team,
  (teamParam) => {
    openTeamFromQuery(teamParam)
  },
)
</script>

<style scoped>
.teams-page {
  gap: 1.2rem;
}

.header-card,
.teams-card {
  padding: 1.2rem;
}

.header-card {
  background:
    linear-gradient(135deg, rgba(13, 148, 136, 0.12), rgba(15, 23, 42, 0.03)),
    #fff;
  border: 1px solid rgba(13, 148, 136, 0.22);
}

.back-link {
  display: inline-block;
  color: var(--brand-700);
  font-weight: 700;
  text-decoration: none;
  margin-bottom: 1rem;
}

.teams-card h2 {
  margin-top: 0;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.team-item {
  border: 1px solid var(--line-soft);
  border-radius: 16px;
  background: #fff;
  padding: 0.9rem;
  transition: box-shadow 0.16s ease, transform 0.16s ease;
}

.team-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
}

.team-item.focused {
  border-color: rgba(13, 148, 136, 0.5);
  box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.18);
}

.team-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.7rem;
}

.team-head h3 {
  margin: 0;
  font-family: var(--font-display);
}

.team-head p {
  margin: 0.25rem 0 0;
}

.team-actions {
  display: flex;
  gap: 0.4rem;
}

.btn-soft {
  border: 1px solid var(--line-strong);
  background: #fff;
  border-radius: 10px;
  padding: 0.4rem 0.65rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.btn-danger {
  border: 1px solid #dc2626;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 10px;
  padding: 0.4rem 0.65rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.members-box {
  margin-top: 0.55rem;
}

.members-box p {
  margin: 0;
}

.member-chips {
  margin-top: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border-radius: 999px;
  padding: 0.3rem 0.55rem;
  background: rgba(20, 184, 166, 0.15);
  color: var(--brand-700);
  font-weight: 600;
}

.chip-remove {
  border: none;
  background: transparent;
  color: #b91c1c;
  cursor: pointer;
  font-weight: 700;
  line-height: 1;
}

.manage-box {
  margin-top: 0.75rem;
  display: grid;
  gap: 0.5rem;
}

.edit-grid {
  margin-top: 0.75rem;
  display: grid;
  gap: 0.6rem;
}

@media (max-width: 900px) {
  .team-grid {
    grid-template-columns: 1fr;
  }
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
  width: min(100%, 480px);
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
  margin: 0.4rem 0 0;
}

.modal-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
}

.btn-cancel {
  border: 1px solid var(--line-strong);
  background: #fff;
  border-radius: 10px;
  padding: 0.4rem 0.65rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}
</style>
