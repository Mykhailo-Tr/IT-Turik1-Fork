<template>
  <section class="page-shell teams-page">
    <article class="card create-card">
      <p class="section-eyebrow">Teams</p>
      <h1 class="section-title">Create new team</h1>
      <p class="section-subtitle">Create a team and optionally add initial members.</p>
      <router-link to="/teams" class="back-link">Back to teams list</router-link>

      <p v-if="notification" :class="['notice', notification.type]">{{ notification.message }}</p>

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
          Telegram
          <input
            v-model="createForm.contact_telegram"
            class="input-control"
            type="text"
            placeholder="@team_username"
            pattern="^@?[A-Za-z][A-Za-z0-9_]{4,31}$"
            title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
          />
        </label>

        <label class="form-label">
          Discord
          <input
            v-model="createForm.contact_discord"
            class="input-control"
            type="text"
            placeholder="team.username"
            pattern="^@?(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?$"
            title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
          />
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
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { API_BASE } from '@/features/shared/config/api'

const router = useRouter()

const createLoading = ref(false)
const notification = ref(null)
const memberSearch = ref('')
const currentUserId = ref(null)
const users = ref([])

const createForm = ref({
  name: '',
  email: '',
  organization: '',
  contact_telegram: '',
  contact_discord: '',
  member_ids: [],
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

const createCandidateUsers = computed(() => {
  const search = memberSearch.value.trim().toLowerCase()
  return users.value.filter((user) => {
    if (user.id === currentUserId.value) return false
    if (!search) return true
    return [user.username, user.email, user.full_name || ''].join(' ').toLowerCase().includes(search)
  })
})

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
    contact_telegram: '',
    contact_discord: '',
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

    const data = await response.json()
    if (!response.ok) {
      notification.value = { type: 'error', message: JSON.stringify(data) }
      return
    }

    notification.value = { type: 'success', message: 'Team created successfully.' }
    resetCreateForm()
    router.push(`/teams/${data.id}`)
  } catch {
    notification.value = { type: 'error', message: 'Server connection error.' }
  } finally {
    createLoading.value = false
  }
}

onMounted(async () => {
  const ok = await fetchProfile()
  if (!ok) return
  await fetchUsers()
})
</script>

<style scoped>
.teams-page {
  gap: 1.2rem;
}

.create-card {
  padding: 1.2rem;
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

@media (max-width: 760px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
