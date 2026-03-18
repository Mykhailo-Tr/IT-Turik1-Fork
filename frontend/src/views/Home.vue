<template>
  <section class="page-shell home-page">
    <article class="card hero">
      <div>
        <p class="eyebrow">Dashboard</p>
        <h1 v-if="userProfile">Welcome back, {{ displayName }}</h1>
        <h1 v-else>Welcome to TournamentOS</h1>
        <p class="sub">Manage your profile and stay ready for upcoming competitions.</p>
      </div>

      <div class="hero-actions">
        <router-link to="/profile" class="ghost-btn">Open profile</router-link>
        <button @click="handleLogout" class="danger-btn">Logout</button>
      </div>
    </article>

    <div v-if="isLoading" class="state-box">Loading profile...</div>
    <div v-else-if="error" class="state-box error">{{ error }}</div>

    <div v-else-if="userProfile" class="grid">
      <article class="card info-card">
        <h2>Account details</h2>
        <p><strong>Username:</strong> {{ userProfile.username }}</p>
        <p><strong>Email:</strong> {{ userProfile.email }}</p>
        <p><strong>Role:</strong> {{ userProfile.role }}</p>
        <p v-if="teamNames"><strong>Teams:</strong> {{ teamNames }}</p>
      </article>

      <article class="card info-card accent">
        <h2>Quick status</h2>
        <ul>
          <li>Profile ready: <span>{{ profileReady ? 'Yes' : 'No' }}</span></li>
          <li>City set: <span>{{ userProfile.city ? 'Yes' : 'No' }}</span></li>
          <li>Phone set: <span>{{ userProfile.phone ? 'Yes' : 'No' }}</span></li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { API_BASE } from '@/config/api'
import { useRouter } from 'vue-router'

const userProfile = ref(null)
const isLoading = ref(true)
const error = ref('')
const router = useRouter()

const displayName = computed(() => userProfile.value?.full_name || userProfile.value?.username || 'User')
const profileReady = computed(() => Boolean(userProfile.value?.full_name && userProfile.value?.city))
const teamNames = computed(() => (userProfile.value?.teams || []).map((team) => team.name).join(', '))

onMounted(async () => {
  const token = localStorage.getItem('access')

  try {
    const response = await fetch(`${API_BASE}/api/accounts/profile/`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    if (response.ok) {
      userProfile.value = await response.json()
      if (userProfile.value.needs_onboarding) {
        localStorage.setItem('needs_onboarding', '1')
        router.push('/complete-profile')
        return
      }
      return
    }

    if (response.status === 401) {
      handleLogout()
      return
    }

    error.value = 'Could not load profile data.'
  } catch {
    error.value = 'Server is unavailable. Please try again later.'
  } finally {
    isLoading.value = false
  }
})

const handleLogout = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  localStorage.removeItem('needs_onboarding')
  router.push('/login')
}
</script>

<style scoped>
.home-page {
  display: grid;
  gap: 1rem;
}

.hero {
  padding: 1.4rem;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  background:
    linear-gradient(130deg, rgba(15, 118, 110, 0.95), rgba(20, 184, 166, 0.88)),
    linear-gradient(45deg, rgba(249, 115, 22, 0.2), transparent);
  color: white;
  border: none;
}

.eyebrow {
  margin: 0;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.75rem;
  opacity: 0.85;
}

h1 {
  margin: 0.45rem 0 0;
  font-family: var(--font-display);
  font-size: clamp(1.4rem, 1.3vw + 1rem, 2rem);
}

.sub {
  margin: 0.5rem 0 0;
  opacity: 0.92;
}

.hero-actions {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.ghost-btn,
.danger-btn {
  border-radius: 999px;
  padding: 0.52rem 0.95rem;
  font: inherit;
  font-weight: 700;
  border: 1px solid rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.12);
  color: white;
  text-decoration: none;
  cursor: pointer;
}

.danger-btn {
  border-color: rgba(254, 202, 202, 0.75);
  background: rgba(220, 38, 38, 0.28);
}

.state-box {
  border-radius: 16px;
  padding: 1rem 1.1rem;
  border: 1px solid var(--line-soft);
  background: var(--surface-strong);
}

.state-box.error {
  border-color: rgba(220, 38, 38, 0.25);
  color: #b91c1c;
  background: rgba(254, 242, 242, 0.9);
}

.grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.info-card {
  padding: 1.2rem;
}

.info-card h2 {
  margin-top: 0;
  font-family: var(--font-display);
}

.info-card p {
  margin: 0.5rem 0;
  color: var(--ink-700);
}

.accent {
  background:
    linear-gradient(160deg, rgba(255, 255, 255, 0.92), rgba(237, 254, 255, 0.95));
}

ul {
  margin: 0.8rem 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.55rem;
}

li {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px dashed var(--line-soft);
  padding-bottom: 0.35rem;
}

li span {
  font-weight: 700;
}

@media (max-width: 760px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-actions {
    justify-content: flex-start;
  }

  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
