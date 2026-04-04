import $api from '@/services'
import type { GetProfileResponse, UpdateProfileBody } from '@/services/accounts/types'
import type { User } from '@/services/dbTypes'
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref<GetProfileResponse | null>(null)
  const isLoaded = ref(false)
  const isLoading = ref(false)
  const isInitialized = ref(false)

  const isLoggedIn = computed(() => !!user.value)

  async function update(data: UpdateProfileBody) {
    await $api.accounts.updateProfile(data)

    await loadUser(true)
  }

  async function loadUser(force = false) {
    if (isLoaded.value && !force) return
    if (!localStorage.getItem('access')) return

    isLoading.value = true
    try {
      const response = await $api.accounts.getProfile()

      user.value = response.data
      isLoaded.value = true
    } catch {
      logout()
    } finally {
      isInitialized.value = true
      isLoading.value = false
    }
  }

  async function login(credentials: { username: User['username']; password: string }) {
    isLoading.value = true
    try {
      const response = await $api.accounts.login(credentials)

      localStorage.setItem('access', response.data.access)
      localStorage.setItem('refresh', response.data.refresh)

      if (response.data.onboarding_required) {
        localStorage.setItem('needs_onboarding', '1')
      } else {
        localStorage.removeItem('needs_onboarding')
      }

      await loadUser(true)

      return response.data
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    user.value = null
    isLoaded.value = false
    isInitialized.value = false
  }

  return { user, isLoggedIn, isLoading, isLoaded, isInitialized, loadUser, update, login, logout }
})
