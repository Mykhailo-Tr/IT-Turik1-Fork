import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { API_BASE } from '@/features/shared/config/api'
import { createAuthHeaders, logoutToLogin as redirectToLogin } from '@/features/shared/lib/auth-session'
import { parseApiError } from '@/features/shared/lib/http-errors'
import { useGlobalNotification } from '@/features/shared/lib/notifications'

export const useTeamsEditPage = () => {
  const route = useRoute()
  const router = useRouter()

  const currentUserId = ref(null)
  const team = ref(null)
  const users = ref([])

  const loading = ref(true)
  const loadError = ref('')
  const saveLoading = ref(false)
  const { showNotification, hideNotification } = useGlobalNotification()

  const form = ref({
    name: '',
    email: '',
    organization: '',
    contact_telegram: '',
    contact_discord: '',
  })

  const memberSearch = ref('')
  const addMemberSelection = ref('')
  const addMemberLoading = ref(false)
  const kickLoadingByUser = ref({})

  const teamId = computed(() => Number(route.params.id))
  const isCaptain = computed(() => Boolean(team.value) && team.value.captain_id === currentUserId.value)

  const filteredMembers = computed(() => {
    if (!team.value) return []
    const search = memberSearch.value.trim().toLowerCase()
    if (!search) return team.value.members

    return team.value.members.filter((member) => {
      return [member.username, member.email, member.full_name || ''].join(' ').toLowerCase().includes(search)
    })
  })

  const availableUsers = computed(() => {
    if (!isCaptain.value || !team.value) return []
    const currentIds = new Set(team.value.members.map((member) => member.id))
    return users.value.filter((user) => !currentIds.has(user.id))
  })

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
      headers: createAuthHeaders(false),
    })

    if (response.status === 401) {
      redirectToLogin(router)
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

    const response = await fetch(`${API_BASE}/api/teams/${teamId.value}/`, {
      headers: createAuthHeaders(false),
    })

    if (response.status === 401) {
      redirectToLogin(router)
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

  const fetchUsers = async () => {
    const response = await fetch(`${API_BASE}/api/accounts/users/`, {
      headers: createAuthHeaders(false),
    })

    if (response.status === 401) {
      redirectToLogin(router)
      return false
    }

    if (!response.ok) {
      showNotification('Unable to load users list.', 'error')
      return false
    }

    users.value = await response.json()
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

    const teamOk = await fetchTeam()
    if (teamOk && isCaptain.value) {
      await fetchUsers()
    }

    loading.value = false
  }

  const saveTeam = async () => {
    if (!team.value || !isCaptain.value) return

    saveLoading.value = true
    hideNotification()

    try {
      const response = await fetch(`${API_BASE}/api/teams/${team.value.id}/`, {
        method: 'PATCH',
        headers: createAuthHeaders(true),
        body: JSON.stringify(form.value),
      })

      if (response.status === 401) {
        redirectToLogin(router)
        return
      }

      if (!response.ok) {
        showNotification(await parseApiError(response, 'Unable to update team.'), 'error')
        return
      }

      router.push(`/teams/${team.value.id}`)
    } catch {
      showNotification('Server connection error.', 'error')
    } finally {
      saveLoading.value = false
    }
  }

  const addMember = async () => {
    if (!team.value || !isCaptain.value) return
    if (!addMemberSelection.value) {
      showNotification('Select a user to add.', 'error')
      return
    }

    addMemberLoading.value = true
    hideNotification()
    try {
      const response = await fetch(`${API_BASE}/api/teams/${team.value.id}/members/`, {
        method: 'POST',
        headers: createAuthHeaders(true),
        body: JSON.stringify({ user_id: Number(addMemberSelection.value) }),
      })

      if (response.status === 401) {
        redirectToLogin(router)
        return
      }

      if (!response.ok) {
        showNotification(await parseApiError(response, 'Unable to add member.'), 'error')
        return
      }

      addMemberSelection.value = ''
      showNotification('Invitation sent.', 'success')
      await Promise.all([fetchTeam(), fetchUsers()])
    } catch {
      showNotification('Server connection error.', 'error')
    } finally {
      addMemberLoading.value = false
    }
  }

  const removeMember = async (member) => {
    if (!member || !team.value || !isCaptain.value) return
    if (member.id === team.value.captain_id) return
    kickLoadingByUser.value = {
      ...kickLoadingByUser.value,
      [member.id]: true,
    }
    hideNotification()

    try {
      const response = await fetch(
        `${API_BASE}/api/teams/${team.value.id}/members/${member.id}/`,
        { method: 'DELETE', headers: createAuthHeaders(false) },
      )

      if (response.status === 401) {
        redirectToLogin(router)
        return
      }

      if (!response.ok && response.status !== 204) {
        showNotification(await parseApiError(response, 'Unable to remove member.'), 'error')
        return
      }

      showNotification('Member removed.', 'success')
      await Promise.all([fetchTeam(), fetchUsers()])
    } catch {
      showNotification('Server connection error.', 'error')
    } finally {
      kickLoadingByUser.value = {
        ...kickLoadingByUser.value,
        [member.id]: false,
      }
    }
  }

  onMounted(loadEditor)

  watch(
    () => route.params.id,
    () => {
      loadEditor()
    },
  )

  return {
    addMember,
    addMemberLoading,
    addMemberSelection,
    availableUsers,
    filteredMembers,
    form,
    isCaptain,
    kickLoadingByUser,
    loadError,
    loading,
    memberSearch,
    removeMember,
    saveLoading,
    saveTeam,
    team,
  }
}

