<template>
  <section class="page-shell teams-page">
    <article class="card header-card">
      <p class="section-eyebrow">Teams</p>
      <h1 class="section-title">Team directory</h1>
      <p class="section-subtitle">Open a team workspace to view details, edit info, and manage members.</p>
      <div class="hero-actions">
        <router-link to="/teams/create" class="btn-primary manage-link">Create new team</router-link>
        <span class="meta-pill">Total teams: {{ teams.length }}</span>
      </div>
    </article>

    <div v-if="notification" :class="['notice', notification.type]">{{ notification.message }}</div>
    <div v-if="loading" class="card state-card text-muted">Loading teams...</div>

    <template v-else>
      <article class="card teams-card">
        <header class="section-head">
          <h2>My teams</h2>
          <span class="text-muted">{{ myTeams.length }} joined</span>
        </header>

        <p v-if="myTeams.length === 0" class="text-muted">You are not a member of any team yet.</p>
        <div v-else class="team-grid">
          <article v-for="team in myTeamsPageItems" :key="`my-${team.id}`" class="team-item">
            <div class="team-meta">
              <h3>{{ team.name }}</h3>
              <span v-if="isCaptain(team)" class="status-badge">Captain</span>
            </div>
            <p class="text-muted">Captain: {{ captainName(team) }}</p>
            <p class="text-muted">Members: {{ team.members.length }}</p>
            <router-link :to="`/teams/${team.id}`" class="btn-soft open-link">Open workspace</router-link>
          </article>
        </div>

        <div v-if="myPages > 1" class="pagination">
          <button class="btn-soft" :disabled="myPage === 1" @click="myPage -= 1" type="button">Prev</button>
          <span>Page {{ myPage }} / {{ myPages }}</span>
          <button class="btn-soft" :disabled="myPage === myPages" @click="myPage += 1" type="button">Next</button>
        </div>
      </article>

      <article class="card teams-card">
        <header class="section-head">
          <h2>Other teams</h2>
          <span class="text-muted">{{ otherTeams.length }} available</span>
        </header>

        <p v-if="otherTeams.length === 0" class="text-muted">No other teams available.</p>
        <div v-else class="team-grid">
          <article v-for="team in otherTeamsPageItems" :key="`other-${team.id}`" class="team-item">
            <div class="team-meta">
              <h3>{{ team.name }}</h3>
            </div>
            <p class="text-muted">Captain: {{ captainName(team) }}</p>
            <p class="text-muted">Members: {{ team.members.length }}</p>
            <router-link :to="`/teams/${team.id}`" class="btn-soft open-link">Open workspace</router-link>
          </article>
        </div>

        <div v-if="otherPages > 1" class="pagination">
          <button class="btn-soft" :disabled="otherPage === 1" @click="otherPage -= 1" type="button">Prev</button>
          <span>Page {{ otherPage }} / {{ otherPages }}</span>
          <button class="btn-soft" :disabled="otherPage === otherPages" @click="otherPage += 1" type="button">Next</button>
        </div>
      </article>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { API_BASE } from '@/features/shared/config/api'

const PER_PAGE = 8

const router = useRouter()
const teams = ref([])
const currentUserId = ref(null)
const loading = ref(true)
const notification = ref(null)

const myPage = ref(1)
const otherPage = ref(1)

const authHeaders = () => {
  const token = localStorage.getItem('access')
  return { Authorization: `Bearer ${token}` }
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

const myTeams = computed(() =>
  teams.value.filter((team) => team.members.some((member) => member.id === currentUserId.value)),
)

const otherTeams = computed(() =>
  teams.value.filter((team) => !team.members.some((member) => member.id === currentUserId.value)),
)

const myPages = computed(() => Math.max(1, Math.ceil(myTeams.value.length / PER_PAGE)))
const otherPages = computed(() => Math.max(1, Math.ceil(otherTeams.value.length / PER_PAGE)))

const myTeamsPageItems = computed(() => {
  const from = (myPage.value - 1) * PER_PAGE
  return myTeams.value.slice(from, from + PER_PAGE)
})

const otherTeamsPageItems = computed(() => {
  const from = (otherPage.value - 1) * PER_PAGE
  return otherTeams.value.slice(from, from + PER_PAGE)
})

watch(myPages, (pageCount) => {
  if (myPage.value > pageCount) myPage.value = pageCount
})

watch(otherPages, (pageCount) => {
  if (otherPage.value > pageCount) otherPage.value = pageCount
})

const fetchProfile = async () => {
  const response = await fetch(`${API_BASE}/api/accounts/profile/`, {
    headers: authHeaders(),
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
    headers: authHeaders(),
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

onMounted(async () => {
  const ok = await fetchProfile()
  if (!ok) {
    loading.value = false
    return
  }

  await fetchTeams()
  loading.value = false
})
</script>

<style scoped>
.teams-page {
  gap: 1.2rem;
}

.header-card,
.teams-card,
.state-card {
  padding: 1.2rem;
}

.header-card {
  background:
    linear-gradient(135deg, rgba(13, 148, 136, 0.12), rgba(15, 23, 42, 0.03)),
    #fff;
  border: 1px solid rgba(13, 148, 136, 0.22);
}

.hero-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  align-items: center;
}

.manage-link {
  display: inline-flex;
  text-decoration: none;
}

.meta-pill {
  border: 1px solid rgba(15, 23, 42, 0.12);
  border-radius: 999px;
  padding: 0.33rem 0.7rem;
  font-size: 0.84rem;
  color: var(--ink-700);
  background: rgba(255, 255, 255, 0.8);
}

.teams-card {
  border: 1px solid rgba(15, 23, 42, 0.09);
}

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

.status-badge {
  border-radius: 999px;
  border: 1px solid rgba(20, 184, 166, 0.4);
  background: rgba(20, 184, 166, 0.15);
  color: var(--brand-700);
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
}

.team-item p {
  margin: 0;
}

.open-link {
  margin-top: 0.3rem;
  text-decoration: none;
  justify-self: start;
}

.pagination {
  margin-top: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
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

.btn-soft:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .section-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
