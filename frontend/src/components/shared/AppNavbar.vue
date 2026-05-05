<template>
  <nav class="main-nav">
    <div class="nav-container">
      <div style="display: flex; justify-content: center; align-items: center; gap: 10px">
        <router-link to="/" class="brand">TournamentOS</router-link>
        <switch-theme-button />
      </div>
      <div class="nav-links">
        <template v-if="!user">
          <router-link to="/login" :class="navItemClass('login')">Login</router-link>
          <router-link to="/register" style="text-decoration: none">
            <ui-button :class="navItemClass('register', true)">Register</ui-button>
          </router-link>
        </template>

        <template v-else>
          <router-link to="/" :class="navItemClass('home')">Home</router-link>
          <router-link to="/teams" :class="navItemClass('teams')">Teams</router-link>
          <router-link to="/profile" :class="navItemClass('profile')">Profile</router-link>
          
          <notification-dropdown />

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
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UiButton from '../UiButton.vue'
import { useUserStore } from '@/stores/user'
import { useProfile } from '@/queries/accounts'
import SwitchThemeButton from './SwitchThemeButton.vue'
import NotificationDropdown from '@/features/notifications/components/NotificationDropdown.vue'

const route = useRoute()
const router = useRouter()
const store = useUserStore()

const { data: user } = useProfile()

const isAdmin = computed(() => user.value?.role === 'admin')


type Section = 'home' | 'teams' | 'profile' | 'admin' | 'login' | 'register'

const navItemClass = (section: Section, cta = false) => ({
  'nav-item': true,
  'nav-cta': cta,
  active: isSectionActive(section),
})

const logout = () => {
  store.logout()
  router.push('/login')
}

const isSectionActive = (section: Section) => {
  const path = route.path

  if (section === 'home') return path === '/'
  if (section === 'teams') return path === '/teams' || path.startsWith('/teams/')
  if (section === 'profile')
    return path === '/profile' || path.startsWith('/profile/') || path === '/complete-profile'
  if (section === 'admin') return path === '/admin/role-codes'

  return false
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
  background: color-mix(in srgb, var(--background) 80%, transparent);
  border-bottom: 1px solid color-mix(in srgb, var(--border) 40%, transparent);
}

.brand {
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 700;
  text-decoration: none;
  color: var(--foreground);
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
  color: var(--foreground);
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
  background: var(--secondary);
}

.nav-item.active {
  background: var(--secondary);
  color: var(--secondary-foreground);
}

.nav-cta {
  color: var(--primary-foreground);
  background: linear-gradient(120deg, var(--brand-700), var(--brand-500));
}

.nav-cta:hover {
  background: linear-gradient(120deg, var(--brand-600), var(--brand-500));
}

.nav-cta.active {
  color: var(--primary-foreground);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.45);
}
</style>
