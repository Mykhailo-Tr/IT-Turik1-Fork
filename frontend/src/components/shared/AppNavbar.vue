<template>
  <nav class="main-nav">
    <div class="nav-container">
      <router-link to="/" class="brand">TournamentOS</router-link>

      <div class="nav-links">
        <template v-if="!auth.isLoggedIn.value">
          <router-link to="/login" :class="navItemClass('login')">Login</router-link>
          <router-link to="/register" style="text-decoration: none">
            <ui-button :class="navItemClass('register', true)">Register</ui-button>
          </router-link>
        </template>

        <template v-else>
          <router-link to="/" :class="navItemClass('home')">Home</router-link>
          <router-link to="/teams" :class="navItemClass('teams')">Teams</router-link>
          <router-link to="/profile" :class="navItemClass('profile')">Profile</router-link>
          <router-link v-if="isAdmin" to="/admin/role-codes" :class="navItemClass('admin')"
            >Admin</router-link
          >
          <ui-button @click="logout" size="sm" variant="danger" class="logout-btn"
            >Logout</ui-button
          >
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useAuth } from '@/composables/useAuth'
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import UiButton from '../UiButton.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuth()

const isAdmin = computed(() => auth.user.value?.role === 'admin')

type Section = 'home' | 'teams' | 'profile' | 'admin' | 'login' | 'register'

const navItemClass = (section: Section, cta = false) => ({
  'nav-item': true,
  'nav-cta': cta,
  active: isSectionActive(section),
})

const isSectionActive = (section: Section) => {
  const path = route.path

  if (section === 'home') return path === '/'
  if (section === 'teams') return path === '/teams' || path.startsWith('/teams/')
  if (section === 'profile')
    return path === '/profile' || path.startsWith('/profile/') || path === '/complete-profile'
  if (section === 'admin') return path === '/admin/role-codes'

  return false
}

const logout = () => {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
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

.brand {
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 700;
  text-decoration: none;
  color: var(--ink-900);
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

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.nav-item {
  border: 100%;
  color: var(--ink-700);
  text-decoration: none;
  font-weight: 700;
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn {
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
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
</style>
