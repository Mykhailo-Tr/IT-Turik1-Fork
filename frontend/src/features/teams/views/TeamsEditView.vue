<template>
  <section class="page-shell teams-edit-page">
    <article class="card hero-card">
      <p class="section-eyebrow">Team workspace</p>
      <h1 class="section-title">Edit {{ team?.name || 'team' }}</h1>
      <div class="hero-actions">
        <router-link :to="team ? `/teams/${team.id}` : '/teams'" class="btn-soft action-link">Back to team</router-link>
      </div>
    </article>

    <div v-if="notification" :class="['notice', notification.type]">{{ notification.message }}</div>

    <div v-if="loading" class="card state-card text-muted">Loading team editor...</div>
    <div v-else-if="loadError" class="card state-card text-error">{{ loadError }}</div>

    <template v-else-if="team">
      <div class="workspace-grid">
        <article class="card panel form-panel">
          <header class="panel-head">
            <h2>Team profile settings</h2>
            <span v-if="isCaptain" class="status-badge">Captain access</span>
          </header>

          <p v-if="!isCaptain" class="notice error lock-note">
            Only team captain can edit this team.
          </p>

          <form class="form-grid" @submit.prevent="saveTeam">
            <label class="form-label">
              Team name
              <input v-model="form.name" class="input-control" type="text" required :disabled="!isCaptain || saveLoading" />
            </label>

            <label class="form-label">
              Team email
              <input
                v-model="form.email"
                class="input-control"
                type="email"
                required
                :disabled="!isCaptain || saveLoading"
              />
            </label>

            <label class="form-label">
              Organization
              <input v-model="form.organization" class="input-control" type="text" :disabled="!isCaptain || saveLoading" />
            </label>

            <label class="form-label">
              Telegram
              <input
                v-model="form.contact_telegram"
                class="input-control"
                type="text"
                pattern="^@?[A-Za-z][A-Za-z0-9_]{4,31}$"
                title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
                :disabled="!isCaptain || saveLoading"
              />
            </label>

            <label class="form-label">
              Discord
              <input
                v-model="form.contact_discord"
                class="input-control"
                type="text"
                pattern="^@?(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?$"
                title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
                :disabled="!isCaptain || saveLoading"
              />
            </label>

            <div class="form-actions full-width">
              <button class="btn-primary" type="submit" :disabled="!isCaptain || saveLoading">
                {{ saveLoading ? 'Saving...' : 'Save changes' }}
              </button>
              <router-link :to="`/teams/${team.id}`" class="btn-soft action-link">Cancel</router-link>
            </div>
          </form>
        </article>

        <article class="card panel members-panel">
          <header class="panel-head">
            <h2>Members management</h2>
            <span class="text-muted">{{ team.members.length }} people</span>
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

          <div class="member-list">
            <article v-for="member in filteredMembers" :key="`member-${member.id}`" class="member-row">
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
                  :disabled="kickLoadingByUser[member.id]"
                  @click="removeMember(member)"
                >
                  {{ kickLoadingByUser[member.id] ? 'Removing...' : 'Remove' }}
                </button>
              </div>
            </article>
          </div>

          <p v-if="filteredMembers.length === 0" class="text-muted member-note">No members match your search.</p>

          <div v-if="isCaptain" class="add-member-box">
            <h3>Invite user</h3>

            <label class="form-label">
              Select user
              <select v-model="addMemberSelection" class="select-control">
                <option value="">Select user</option>
                <option v-for="user in availableUsers" :key="`add-${user.id}`" :value="String(user.id)">
                  {{ user.username }} ({{ user.email }})
                </option>
              </select>
            </label>

            <p v-if="availableUsers.length === 0" class="text-muted">No available users to add.</p>

            <button class="btn-primary" type="button" @click="addMember" :disabled="addMemberLoading">
              {{ addMemberLoading ? 'Sending...' : 'Send invitation' }}
            </button>
          </div>

          <div v-if="isCaptain" class="add-member-box">
            <h3>Invitations status</h3>
            <p v-if="!team.invitations?.length" class="text-muted">No invitations yet.</p>
            <div v-else class="member-list">
              <article v-for="invitation in team.invitations" :key="`inv-${invitation.id}`" class="member-row">
                <div>
                  <p class="member-name">{{ invitation.user.username }}</p>
                  <p class="text-muted member-email">{{ invitation.user.email }}</p>
                </div>
                <span class="captain-tag">{{ invitation.status }}</span>
              </article>
            </div>
          </div>
        </article>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { API_BASE } from '@/features/shared/config/api'

const route = useRoute()
const router = useRouter()

const currentUserId = ref(null)
const team = ref(null)
const users = ref([])

const loading = ref(true)
const loadError = ref('')
const notification = ref(null)
const saveLoading = ref(false)

const form = ref({
  name: '',
  email: '',
  organization: '',
  contact_telegram: '',
  contact_discord: '',
})

const memberSearch = ref('')
const addMemberSelection = ref('')
const addMemberLoading = ref(false)
const kickLoadingByUser = ref({})

const teamId = computed(() => Number(route.params.id))
const isCaptain = computed(() => Boolean(team.value) && team.value.captain_id === currentUserId.value)

const filteredMembers = computed(() => {
  if (!team.value) return []
  const search = memberSearch.value.trim().toLowerCase()
  if (!search) return team.value.members

  return team.value.members.filter((member) => {
    return [member.username, member.email, member.full_name || ''].join(' ').toLowerCase().includes(search)
  })
})

const availableUsers = computed(() => {
  if (!isCaptain.value || !team.value) return []
  const currentIds = new Set(team.value.members.map((member) => member.id))
  return users.value.filter((user) => !currentIds.has(user.id))
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

const fillForm = () => {
  if (!team.value) return
  form.value = {
    name: team.value.name || '',
    email: team.value.email || '',
    organization: team.value.organization || '',
    contact_telegram: team.value.contact_telegram || '',
    contact_discord: team.value.contact_discord || '',
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
  fillForm()
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

const loadEditor = async () => {
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

const saveTeam = async () => {
  if (!team.value || !isCaptain.value) return

  saveLoading.value = true
  notification.value = null

  try {
    const response = await fetch(`${API_BASE}/api/accounts/teams/${team.value.id}/`, {
      method: 'PATCH',
      headers: authHeaders(true),
      body: JSON.stringify(form.value),
    })

    if (response.status === 401) {
      logoutToLogin()
      return
    }

    if (!response.ok) {
      notification.value = { type: 'error', message: await parseApiError(response, 'Unable to update team.') }
      return
    }

    router.push(`/teams/${team.value.id}`)
  } catch {
    notification.value = { type: 'error', message: 'Server connection error.' }
  } finally {
    saveLoading.value = false
  }
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
    notification.value = { type: 'success', message: 'Invitation sent.' }
    await Promise.all([fetchTeam(), fetchUsers()])
  } catch {
    notification.value = { type: 'error', message: 'Server connection error.' }
  } finally {
    addMemberLoading.value = false
  }
}

const removeMember = async (member) => {
  if (!member || !team.value || !isCaptain.value) return
  if (member.id === team.value.captain_id) return
  kickLoadingByUser.value = {
    ...kickLoadingByUser.value,
    [member.id]: true,
  }
  notification.value = null

  try {
    const response = await fetch(
      `${API_BASE}/api/accounts/teams/${team.value.id}/members/${member.id}/`,
      { method: 'DELETE', headers: authHeaders(false) },
    )

    if (response.status === 401) {
      logoutToLogin()
      return
    }

    if (!response.ok && response.status !== 204) {
      notification.value = { type: 'error', message: await parseApiError(response, 'Unable to remove member.') }
      return
    }

    notification.value = { type: 'success', message: 'Member removed.' }
    await Promise.all([fetchTeam(), fetchUsers()])
  } catch {
    notification.value = { type: 'error', message: 'Server connection error.' }
  } finally {
    kickLoadingByUser.value = {
      ...kickLoadingByUser.value,
      [member.id]: false,
    }
  }
}

onMounted(loadEditor)

watch(
  () => route.params.id,
  () => {
    loadEditor()
  },
)
</script>

<style scoped>
.teams-edit-page {
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
  margin-top: 0.8rem;
}

.action-link {
  text-decoration: none;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  align-items: start;
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

.lock-note {
  margin-top: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.full-width {
  grid-column: 1 / -1;
}

.form-actions {
  display: flex;
  gap: 0.6rem;
  align-items: center;
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

.captain-tag {
  border-radius: 999px;
  border: 1px solid rgba(14, 116, 144, 0.35);
  background: rgba(14, 116, 144, 0.14);
  color: #0e7490;
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
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

@media (max-width: 760px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .member-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
