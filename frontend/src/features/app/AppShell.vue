<template>
  <div id="app" class="app-shell">
    <div class="bg-orb orb-a"></div>
    <div class="bg-orb orb-b"></div>

    <nav class="main-nav">
      <div class="nav-container">
        <router-link to="/" class="brand">TournamentOS</router-link>

        <div class="nav-links">
          <router-link to="/" :class="navItemClass('home')">Home</router-link>

          <template v-if="!isLoggedIn">
            <router-link to="/login" :class="navItemClass('login')">Sign in</router-link>
            <router-link to="/register" :class="navItemClass('register', true)">Register</router-link>
          </template>

          <template v-else>
            <router-link to="/teams" :class="navItemClass('teams')">Teams</router-link>
            <router-link to="/profile" :class="navItemClass('profile')">Profile</router-link>
            <button @click="logout" class="nav-item nav-danger">Logout</button>
          </template>
        </div>
      </div>
    </nav>

    <Transition name="global-notice" mode="out-in">
      <div
        v-if="notification"
        :key="notification.id"
        :class="['notice', 'app-notice', notification.type, `type-${notification.type}`]"
        role="status"
        aria-live="polite"
      >
        <span>{{ notification.message }}</span>
        <button type="button" class="app-notice-close" @click="hideNotification()">Dismiss</button>
      </div>
    </Transition>

    <main class="page-content">
      <router-view @auth-change="checkAuth" />
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGlobalNotification } from '@/features/shared/lib/notifications'

const isLoggedIn = ref(false)
const router = useRouter()
const route = useRoute()
const { notification, hideNotification } = useGlobalNotification()

const checkAuth = () => {
  isLoggedIn.value = !!localStorage.getItem('access')
}

const isSectionActive = (section) => {
  const path = route.path

  if (section === 'home') {
    return path === '/'
  }

  if (section === 'teams') {
    return path === '/teams' || path.startsWith('/teams/')
  }

  if (section === 'profile') {
    return path === '/profile' || path.startsWith('/profile/') || path === '/complete-profile'
  }

  if (section === 'login') {
    return path === '/login' || path.startsWith('/activate/')
  }

  if (section === 'register') {
    return path === '/register'
  }

  return false
}

const navItemClass = (section, cta = false) => ({
  'nav-item': true,
  'nav-cta': cta,
  active: isSectionActive(section),
})

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
  --nav-offset: 76px;
  position: relative;
  min-height: 100vh;
  overflow-x: hidden;
  padding-top: var(--nav-offset);
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
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
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

.nav-item.active {
  background: rgba(15, 23, 42, 0.1);
  color: var(--ink-900);
}

.nav-cta {
  color: white;
  background: linear-gradient(120deg, var(--brand-700), var(--brand-500));
}

.nav-cta:hover {
  background: linear-gradient(120deg, var(--brand-600), var(--brand-500));
}

.nav-cta.active {
  color: white;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.45);
}

.nav-danger {
  color: #b91c1c;
}

.page-content {
  width: min(1100px, 100% - 2rem);
  margin: 1.6rem auto 2.4rem;
}

.app-notice {
  position: fixed;
  top: 1rem;
  right: 1rem;
  margin: 0;
  width: min(92vw, 420px);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.7rem;
  z-index: 2000;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.24);
}

.app-notice-close {
  border: 0;
  background: transparent;
  color: inherit;
  font-weight: 700;
  font-size: 0.78rem;
  cursor: pointer;
  opacity: 0.75;
}

.app-notice-close:hover {
  opacity: 1;
}

.type-info {
  color: #0f3a58;
  background: #ecfeff;
  border-color: #7dd3fc;
}

.type-warning {
  color: #92400e;
  background: #fffbeb;
  border-color: #fcd34d;
}

.global-notice-enter-active,
.global-notice-leave-active {
  transition: opacity 220ms ease, transform 220ms ease;
}

.global-notice-enter-from,
.global-notice-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.global-notice-enter-to,
.global-notice-leave-from {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 680px) {
  .app-shell {
    --nav-offset: 122px;
  }

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

  .app-notice {
    top: 0.75rem;
    left: 0.75rem;
    right: 0.75rem;
    width: auto;
  }
}
</style>
