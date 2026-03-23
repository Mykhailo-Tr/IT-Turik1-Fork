<template>
  <section class="page-shell teams-page">
    <article class="card header-card">
      <p class="section-eyebrow">Teams</p>
      <h1 class="section-title">Team directory</h1>
      <p class="section-subtitle">Browse all teams. Your teams are shown first.</p>
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
          <router-link to="/teams/edit" class="btn-soft section-btn">Manage teams</router-link>
        </header>
        <p v-if="myTeams.length === 0" class="text-muted">You are not a member of any team yet.</p>
        <div v-else class="team-grid">
          <article
            v-for="team in myTeamsPageItems"
            :id="`team-view-${team.id}`"
            :key="`my-${team.id}`"
            :class="['team-item', { focused: focusedTeamId === team.id }]"
          >
            <header class="team-head">
              <div>
                <h3>{{ team.name }}</h3>
                <p class="text-muted">Captain: {{ captainName(team) }}</p>
              </div>
              <router-link
                v-if="isCaptain(team)"
                :to="`/teams/edit?team=${team.id}`"
                class="btn-soft edit-link"
              >
                Edit team
              </router-link>
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
        </header>
        <p v-if="otherTeams.length === 0" class="text-muted">No other teams available.</p>
        <div v-else class="team-grid">
          <article
            v-for="team in otherTeamsPageItems"
            :id="`team-view-${team.id}`"
            :key="`other-${team.id}`"
            :class="['team-item', { focused: focusedTeamId === team.id }]"
          >
            <header class="team-head">
              <div>
                <h3>{{ team.name }}</h3>
                <p class="text-muted">Captain: {{ captainName(team) }}</p>
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
import { useRoute, useRouter } from 'vue-router'

import { API_BASE } from '@/features/shared/config/api'

const PER_PAGE = 6

const router = useRouter()
const route = useRoute()
const teams = ref([])
const currentUserId = ref(null)
const loading = ref(true)
const notification = ref(null)
const focusedTeamId = ref(null)

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
  if (myPage.value > pageCount) {
    myPage.value = pageCount
  }
})
watch(otherPages, (pageCount) => {
  if (otherPage.value > pageCount) {
    otherPage.value = pageCount
  }
})

const telegramLink = (username) => `https://t.me/${String(username || '').replace(/^@/, '')}`
const discordLink = (username) => `https://discord.com/users/@${encodeURIComponent(String(username || '').replace(/^@/, ''))}`

const focusTeamCard = (teamId) => {
  focusedTeamId.value = teamId
  requestAnimationFrame(() => {
    const el = document.getElementById(`team-view-${teamId}`)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  })
}

const openTeamFromQuery = (teamParam) => {
  const teamId = Number(teamParam)
  if (!teamId) {
    focusedTeamId.value = null
    return
  }

  const exists = teams.value.some((team) => team.id === teamId)
  if (!exists) {
    return
  }

  const inMyTeams = myTeams.value.some((team) => team.id === teamId)
  if (inMyTeams) {
    const index = myTeams.value.findIndex((team) => team.id === teamId)
    myPage.value = Math.floor(index / PER_PAGE) + 1
  } else {
    const index = otherTeams.value.findIndex((team) => team.id === teamId)
    otherPage.value = Math.floor(index / PER_PAGE) + 1
  }

  focusTeamCard(teamId)
}

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

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  margin-bottom: 0.6rem;
}

.section-head h2 {
  margin: 0;
}

.section-btn {
  text-decoration: none;
}

.teams-card {
  border: 1px solid rgba(15, 23, 42, 0.09);
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
  transition: transform 0.16s ease, box-shadow 0.16s ease;
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

.edit-link {
  text-decoration: none;
  white-space: nowrap;
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

@media (max-width: 900px) {
  .team-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .section-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
