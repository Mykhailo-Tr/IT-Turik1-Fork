<template>
  <section class="page-shell teams-detail-page">
    <article class="card hero-card">
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
            <svg viewBox="0 0 24 24" class="contact-icon" aria-hidden="true">
              <path
                d="M9.04 15.57 8.9 19.47c.45 0 .64-.19.87-.43l2.09-1.98 4.34 3.17c.8.44 1.36.21 1.57-.74l2.85-13.37h.01c.25-1.15-.42-1.6-1.2-1.31L2.64 11.2c-1.12.44-1.1 1.07-.2 1.35l4.8 1.5L18.4 6.9c.53-.35 1.02-.16.62.2L9.04 15.57z"
                fill="currentColor"
              />
            </svg>
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
            <svg viewBox="0 0 24 24" class="contact-icon" aria-hidden="true">
              <path
                d="M20.32 4.37A19.8 19.8 0 0 0 15.3 3l-.27.54a18.7 18.7 0 0 1 4.82 1.48c-2.97-1.39-6.16-2.1-9.36-2.05-3.2-.05-6.39.66-9.36 2.05a18.7 18.7 0 0 1 4.82-1.48L5.68 3A19.8 19.8 0 0 0 .66 4.37C-2.53 9.1-3.39 13.7-2.97 18.22a19.9 19.9 0 0 0 6.11 3.08l1.31-1.8c-.72-.27-1.4-.6-2.04-.98.17.12.36.23.55.34 3.84 2.1 8 2.1 11.84 0 .19-.11.38-.22.55-.34-.64.38-1.32.71-2.04.98l1.31 1.8a19.9 19.9 0 0 0 6.11-3.08c.5-5.29-.86-9.86-3.4-13.85ZM8.02 15.45c-1.2 0-2.17-1.1-2.17-2.45 0-1.36.95-2.45 2.17-2.45 1.22 0 2.2 1.1 2.17 2.45 0 1.35-.95 2.45-2.17 2.45Zm7.96 0c-1.2 0-2.17-1.1-2.17-2.45 0-1.36.95-2.45 2.17-2.45 1.22 0 2.2 1.1 2.17 2.45 0 1.35-.95 2.45-2.17 2.45Z"
                fill="currentColor"
              />
            </svg>
            <span>{{ team.contact_discord }}</span>
          </a>

          <span v-else class="contact-pill muted">No Discord</span>
        </div>
      </div>

      <div class="hero-actions">
        <router-link to="/teams" class="btn-soft action-link">Back to teams</router-link>
      </div>
    </article>

    <div v-if="notification" :class="['notice', notification.type]">{{ notification.message }}</div>

    <div v-if="loading" class="card state-card text-muted">Loading team workspace...</div>
    <div v-else-if="loadError" class="card state-card text-error">{{ loadError }}</div>

    <template v-else-if="team">
      <div class="workspace-grid">
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

        <article class="card panel members-panel">
          <header class="panel-head">
            <h2>Members</h2>
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
              <span v-if="member.id === team.captain_id" class="captain-tag">Captain</span>
            </article>
          </div>

          <p v-if="filteredMembers.length === 0" class="text-muted member-note">No members match your search.</p>
        </article>
      </div>

      <article v-if="isCaptain" class="card manage-zone">
        <div class="manage-row">
          <div>
            <h3>Edit team</h3>
            <p class="text-muted">Update team profile and manage members in edit workspace.</p>
          </div>
          <router-link :to="`/teams/${team.id}/edit`" class="btn-soft action-link action-btn">Edit team</router-link>
        </div>

        <div class="manage-row danger">
          <div>
            <h3>Delete team</h3>
            <p class="text-muted">This action permanently deletes the team.</p>
          </div>
          <button class="btn-danger" type="button" :disabled="deleteTeamLoading" @click="openDeleteModal">
            Delete team
          </button>
        </div>
      </article>
    </template>

    <div v-if="isDeleteModalOpen" class="modal-backdrop" @click.self="closeDeleteModal">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="delete-team-title">
        <h3 id="delete-team-title">Delete team</h3>
        <p class="modal-text">
          This action cannot be undone. Enter
          <code>{{ expectedDeleteText }}</code>
          to confirm.
        </p>

        <input
          v-model="deleteConfirmInput"
          class="input-control"
          type="text"
          :placeholder="expectedDeleteText"
          :disabled="deleteTeamLoading"
        />

        <p v-if="deleteError" class="text-error modal-error">{{ deleteError }}</p>

        <div class="modal-actions">
          <button class="btn-cancel" type="button" :disabled="deleteTeamLoading" @click="closeDeleteModal">
            Cancel
          </button>
          <button class="btn-danger" type="button" :disabled="!canDeleteTeam" @click="confirmDeleteTeam">
            {{ deleteTeamLoading ? 'Deleting...' : 'Delete permanently' }}
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
const currentUserId = ref(null)

const loading = ref(true)
const loadError = ref('')
const notification = ref(null)

const memberSearch = ref('')
const isDeleteModalOpen = ref(false)
const deleteConfirmInput = ref('')
const deleteTeamLoading = ref(false)
const deleteError = ref('')

const teamId = computed(() => Number(route.params.id))
const isCaptain = computed(() => Boolean(team.value) && team.value.captain_id === currentUserId.value)

const captainName = computed(() => {
  if (!team.value) return '-'
  const captain = team.value.members.find((member) => member.id === team.value.captain_id)
  return captain?.username || `User #${team.value.captain_id}`
})

const filteredMembers = computed(() => {
  if (!team.value) return []
  const search = memberSearch.value.trim().toLowerCase()
  if (!search) return team.value.members

  return team.value.members.filter((member) => {
    return [member.username, member.email, member.full_name || ''].join(' ').toLowerCase().includes(search)
  })
})

const expectedDeleteText = computed(() => team.value?.name || '')
const canDeleteTeam = computed(() => {
  return Boolean(expectedDeleteText.value) && deleteConfirmInput.value === expectedDeleteText.value && !deleteTeamLoading.value
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

const loadWorkspace = async () => {
  loading.value = true
  loadError.value = ''
  isDeleteModalOpen.value = false
  deleteConfirmInput.value = ''
  deleteError.value = ''

  const profileOk = await fetchProfile()
  if (!profileOk) {
    loading.value = false
    return
  }

  await fetchTeam()
  loading.value = false
}

const openDeleteModal = () => {
  deleteConfirmInput.value = ''
  deleteError.value = ''
  isDeleteModalOpen.value = true
}

const closeDeleteModal = () => {
  if (deleteTeamLoading.value) return
  isDeleteModalOpen.value = false
}

const confirmDeleteTeam = async () => {
  if (!team.value) return
  if (!canDeleteTeam.value) {
    deleteError.value = `Please enter "${expectedDeleteText.value}" exactly.`
    return
  }

  deleteTeamLoading.value = true
  deleteError.value = ''
  notification.value = null
  try {
    const response = await fetch(`${API_BASE}/api/accounts/teams/${team.value.id}/`, {
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
.panel,
.manage-zone {
  padding: 1.2rem;
}

.hero-card {
  background:
    linear-gradient(135deg, rgba(13, 148, 136, 0.14), rgba(15, 23, 42, 0.03)),
    #fff;
  border: 1px solid rgba(13, 148, 136, 0.22);
}

.hero-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.hero-contacts {
  display: grid;
  gap: 0.45rem;
  justify-items: end;
}

.contact-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border: 1px solid var(--line-soft);
  border-radius: 999px;
  background: #fff;
  padding: 0.25rem 0.6rem;
  font-size: 0.84rem;
  text-decoration: none;
  color: var(--ink-800);
  max-width: 100%;
}

.contact-pill.muted {
  color: var(--ink-500);
}

.contact-icon {
  width: 1rem;
  height: 1rem;
  color: var(--brand-700);
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
  grid-template-columns: 0.95fr 1.25fr;
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

.info-grid {
  display: grid;
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

.manage-zone {
  border: 1px solid var(--line-soft);
  overflow: hidden;
}

.manage-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.9rem;
  padding: 1rem 0;
}

.manage-row + .manage-row {
  border-top: 1px solid var(--line-soft);
}

.manage-row h3 {
  margin: 0;
  font-size: 1rem;
}

.manage-row p {
  margin: 0.3rem 0 0;
}

.manage-row.danger h3 {
  color: #991b1b;
}

.action-btn {
  font-weight: 700;
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
  width: min(100%, 520px);
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

.modal-text code {
  background: #f1f5f9;
  border: 1px solid var(--line-soft);
  border-radius: 6px;
  padding: 0.1rem 0.35rem;
}

.modal-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
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

.btn-danger:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-cancel {
  border: 1px solid var(--line-strong);
  border-radius: 10px;
  padding: 0.45rem 0.7rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
  background: #fff;
}

.modal-error {
  margin: 0.5rem 0 0;
}

@media (max-width: 1020px) {
  .hero-top {
    flex-direction: column;
  }

  .hero-contacts {
    justify-items: start;
  }

  .workspace-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .member-row,
  .manage-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
