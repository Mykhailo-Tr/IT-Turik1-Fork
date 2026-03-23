<template>
  <div id="app" class="app-shell">
    <div class="bg-orb orb-a"></div>
    <div class="bg-orb orb-b"></div>

    <nav class="main-nav">
      <div class="nav-container">
        <router-link to="/" class="brand">TournamentOS</router-link>

        <div class="nav-links">
          <router-link to="/" class="nav-item">Home</router-link>

          <template v-if="!isLoggedIn">
            <router-link to="/login" class="nav-item">Sign in</router-link>
            <router-link to="/register" class="nav-item nav-cta">Register</router-link>
          </template>

          <template v-else>
            <router-link to="/teams" class="nav-item">Teams</router-link>
            <router-link to="/profile" class="nav-item">Profile</router-link>
            <button @click="logout" class="nav-item nav-danger">Logout</button>
          </template>
        </div>
      </div>
    </nav>

    <main class="page-content">
      <router-view @auth-change="checkAuth" />
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const isLoggedIn = ref(false)
const router = useRouter()
const route = useRoute()

const checkAuth = () => {
  isLoggedIn.value = !!localStorage.getItem('access')
}

watch(
  () => route.path,
  () => {
    checkAuth()
  },
)

onMounted(() => {
  checkAuth()
})

const logout = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  localStorage.removeItem('needs_onboarding')
  checkAuth()
  router.push('/login')
}
</script>

<style scoped>
.app-shell {
  position: relative;
  min-height: 100vh;
  overflow-x: hidden;
}

.bg-orb {
  position: fixed;
  border-radius: 999px;
  filter: blur(40px);
  z-index: -1;
  pointer-events: none;
}

.orb-a {
  width: 320px;
  height: 320px;
  left: -90px;
  top: 80px;
  background: rgba(20, 184, 166, 0.18);
}

.orb-b {
  width: 260px;
  height: 260px;
  right: -70px;
  top: 220px;
  background: rgba(249, 115, 22, 0.18);
}

.main-nav {
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(10px);
  background: rgba(248, 250, 252, 0.8);
  border-bottom: 1px solid var(--line-soft);
}

.nav-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0.9rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.brand {
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 700;
  text-decoration: none;
  color: var(--ink-900);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.nav-item {
  border: none;
  background: transparent;
  color: var(--ink-700);
  text-decoration: none;
  font-weight: 700;
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: rgba(15, 23, 42, 0.06);
}

.nav-cta {
  color: white;
  background: linear-gradient(120deg, var(--brand-700), var(--brand-500));
}

.nav-cta:hover {
  background: linear-gradient(120deg, var(--brand-600), var(--brand-500));
}

.nav-danger {
  color: #b91c1c;
}

.page-content {
  width: min(1100px, 100% - 2rem);
  margin: 1.6rem auto 2.4rem;
}

@media (max-width: 680px) {
  .nav-container {
    align-items: flex-start;
    flex-direction: column;
  }

  .nav-links {
    width: 100%;
    justify-content: flex-start;
  }

  .page-content {
    width: min(1100px, 100% - 1rem);
    margin-top: 1rem;
  }
}
</style>

