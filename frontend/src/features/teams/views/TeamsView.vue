<template>
  <section class="page-shell teams-page">
    <article class="card create-card">
      <p class="section-eyebrow">Teams</p>
      <h1 class="section-title">Team management</h1>
      <p class="section-subtitle">Create a team, assign members, and manage captain-owned teams.</p>

      <div v-if="notification" :class="['notice', notification.type]">{{ notification.message }}</div>

      <form class="form-grid" @submit.prevent="handleCreateTeam">
        <label class="form-label">
          Team name
          <input v-model="createForm.name" class="input-control" type="text" required />
        </label>

        <label class="form-label">
          Team email
          <input v-model="createForm.email" class="input-control" type="email" required />
        </label>

        <label class="form-label">
          Organization
          <input v-model="createForm.organization" class="input-control" type="text" />
        </label>

        <label class="form-label">
          Contact
          <input v-model="createForm.contact" class="input-control" type="text" />
        </label>

        <div class="full-width">
          <label class="form-label">
            Add initial members
            <input
              v-model="memberSearch"
              class="input-control"
              type="text"
              placeholder="Search by username, email, full name"
            />
          </label>

          <div class="member-picker">
            <label v-for="user in createCandidateUsers" :key="`create-${user.id}`" class="picker-item">
              <input v-model="createForm.member_ids" type="checkbox" :value="user.id" />
              <span>{{ user.username }} ({{ user.email }})</span>
            </label>
            <p v-if="createCandidateUsers.length === 0" class="text-muted empty-note">No users found.</p>
          </div>
        </div>

        <button class="btn-primary full-width" :disabled="createLoading" type="submit">
          {{ createLoading ? 'Creating...' : 'Create team' }}
        </button>
      </form>
    </article>

    <article class="card teams-card">
      <h2>All teams</h2>
      <p v-if="loading" class="text-muted">Loading teams...</p>
      <p v-else-if="teams.length === 0" class="text-muted">No teams yet.</p>

      <div v-else class="team-grid">
        <article v-for="team in teams" :key="team.id" class="team-item">
          <header class="team-head">
            <div>
              <h3>{{ team.name }}</h3>
              <p class="text-muted">Captain: {{ captainName(team) }}</p>
            </div>

            <div v-if="isCaptain(team)" class="team-actions">
              <button class="btn-soft" type="button" @click="toggleEdit(team)">
                {{ isEditing(team.id) ? 'Cancel edit' : 'Edit' }}
              </button>
              <button class="btn-danger" type="button" @click="openDeleteModal(team)">Delete</button>
            </div>
          </header>

          <p><strong>Email:</strong> {{ team.email }}</p>
          <p><strong>Organization:</strong> {{ team.organization || '-' }}</p>
          <p><strong>Contact:</strong> {{ team.contact || '-' }}</p>

          <div class="members-box">
            <p><strong>Members:</strong></p>
            <div class="member-chips">
              <span v-for="member in team.members" :key="`team-${team.id}-member-${member.id}`" class="chip">
                {{ member.username }}
                <button
                  v-if="isCaptain(team) && member.id !== team.captain_id"
                  type="button"
                  class="chip-remove"
                  @click="openKickModal(team, member)"
                >
                  x
                </button>
              </span>
            </div>
          </div>

          <div v-if="isCaptain(team)" class="manage-box">
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
              Contact
              <input v-model="editForms[team.id].contact" class="input-control" type="text" />
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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { API_BASE } from '@/features/shared/config/api'

const router = useRouter()

const teams = ref([])
const users = ref([])
const loading = ref(true)
const createLoading = ref(false)
const notification = ref(null)
const memberSearch = ref('')
const currentUserId = ref(null)

const createForm = ref({
  name: '',
  email: '',
  organization: '',
  contact: '',
  member_ids: [],
})

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

const authHeaders = (json = false) => {
  const token = localStorage.getItem('access')
  const headers = { Authorization: `Bearer ${token}` }
  if (json) {
    headers['Content-Type'] = 'application/json'
  }
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

const isCaptain = (team) => team.captain_id === currentUserId.value
const isEditing = (teamId) => Boolean(editState.value[teamId])

const createCandidateUsers = computed(() => {
  const search = memberSearch.value.trim().toLowerCase()
  return users.value.filter((user) => {
    if (user.id === currentUserId.value) {
      return false
    }

    if (!search) {
      return true
    }

    return [user.username, user.email, user.full_name || ''].join(' ').toLowerCase().includes(search)
  })
})

const availableUsersForTeam = (team) => {
  const currentIds = new Set(team.members.map((member) => member.id))
  return users.value.filter((user) => !currentIds.has(user.id))
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

const resetCreateForm = () => {
  createForm.value = {
    name: '',
    email: '',
    organization: '',
    contact: '',
    member_ids: [],
  }
}

const handleCreateTeam = async () => {
  createLoading.value = true
  notification.value = null

  try {
    const response = await fetch(`${API_BASE}/api/accounts/teams/`, {
      method: 'POST',
      headers: authHeaders(true),
      body: JSON.stringify(createForm.value),
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

    notification.value = { type: 'success', message: 'Team created successfully.' }
    resetCreateForm()
    await fetchTeams()
  } catch {
    notification.value = { type: 'error', message: 'Server connection error.' }
  } finally {
    createLoading.value = false
  }
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
    contact: team.contact || '',
  }
}

const saveTeam = async (teamId) => {
  const payload = editForms.value[teamId]
  if (!payload) {
    return
  }

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
  if (kickLoading.value && !force) {
    return
  }
  isKickModalOpen.value = false
  memberPendingKick.value = null
}

const confirmKickMember = async () => {
  if (!memberPendingKick.value) {
    return
  }

  kickLoading.value = true
  kickError.value = ''
  notification.value = null
  try {
    const response = await fetch(
      `${API_BASE}/api/accounts/teams/${memberPendingKick.value.teamId}/members/${memberPendingKick.value.userId}/`,
      {
      method: 'DELETE',
      headers: authHeaders(false),
      },
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
  if (deleteTeamLoading.value && !force) {
    return
  }
  isDeleteModalOpen.value = false
  teamPendingDelete.value = null
}

const confirmDeleteTeam = async () => {
  if (!teamPendingDelete.value) {
    return
  }

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
  loading.value = false
})
</script>

<style scoped>
.teams-page {
  gap: 1.2rem;
}

.create-card,
.teams-card {
  padding: 1.2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.full-width {
  grid-column: 1 / -1;
}

.member-picker {
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  background: #fff;
  padding: 0.6rem;
  max-height: 180px;
  overflow: auto;
  display: grid;
  gap: 0.45rem;
}

.picker-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--ink-800);
}

.empty-note {
  margin: 0;
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

@media (max-width: 760px) {
  .form-grid {
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

