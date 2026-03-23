<template>
  <section class="page-shell teams-edit-page">
    <article class="card hero-card">
      <p class="section-eyebrow">Team workspace</p>
      <h1 class="section-title">Edit {{ team?.name || 'team' }}</h1>
      <p class="section-subtitle">Update team information. Member management stays in the team detail page.</p>
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

        <aside class="card panel side-panel">
          <header class="panel-head">
            <h2>Workspace overview</h2>
          </header>

          <div class="side-list">
            <div class="side-item">
              <span>Captain</span>
              <strong>{{ captainName }}</strong>
            </div>
            <div class="side-item">
              <span>Members</span>
              <strong>{{ team.members.length }}</strong>
            </div>
            <div class="side-item">
              <span>Telegram</span>
              <strong>{{ team.contact_telegram ? `@${team.contact_telegram}` : '-' }}</strong>
            </div>
            <div class="side-item">
              <span>Discord</span>
              <strong>{{ team.contact_discord || '-' }}</strong>
            </div>
          </div>

          <router-link :to="`/teams/${team.id}`" class="btn-soft side-link">Go to members management</router-link>
        </aside>
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

const teamId = computed(() => Number(route.params.id))
const isCaptain = computed(() => Boolean(team.value) && team.value.captain_id === currentUserId.value)

const captainName = computed(() => {
  if (!team.value) return '-'
  const captain = team.value.members.find((member) => member.id === team.value.captain_id)
  return captain?.username || `User #${team.value.captain_id}`
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

const loadEditor = async () => {
  loading.value = true
  loadError.value = ''

  const profileOk = await fetchProfile()
  if (!profileOk) {
    loading.value = false
    return
  }

  await fetchTeam()
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

    notification.value = { type: 'success', message: 'Team updated successfully.' }
    await fetchTeam()
  } catch {
    notification.value = { type: 'error', message: 'Server connection error.' }
  } finally {
    saveLoading.value = false
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
}

.action-link {
  text-decoration: none;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 1.4fr 0.8fr;
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

.side-panel {
  display: grid;
  gap: 0.8rem;
}

.side-list {
  display: grid;
  gap: 0.55rem;
}

.side-item {
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
  padding: 0.7rem;
}

.side-item span {
  display: block;
  color: var(--ink-500);
  font-size: 0.8rem;
}

.side-item strong {
  color: var(--ink-900);
}

.side-link {
  justify-self: start;
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

@media (max-width: 1020px) {
  .workspace-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
