import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { API_BASE } from '@/features/shared/config/api'
import { createAuthHeaders, logoutToLogin as redirectToLogin } from '@/features/shared/lib/auth-session'
import { useGlobalNotification } from '@/features/shared/lib/notifications'

export const useTeamsCreatePage = () => {
  const router = useRouter()

  const createLoading = ref(false)
  const memberSearch = ref('')
  const currentUserId = ref(null)
  const users = ref([])
  const { showNotification, hideNotification } = useGlobalNotification()

  const createForm = ref({
    name: '',
    email: '',
    organization: '',
    contact_telegram: '',
    contact_discord: '',
    is_public: false,
    member_ids: [],
  })

  const createCandidateUsers = computed(() => {
    const search = memberSearch.value.trim().toLowerCase()
    return users.value.filter((user) => {
      if (user.id === currentUserId.value) return false
      if (!search) return true
      return [user.username, user.email, user.full_name || ''].join(' ').toLowerCase().includes(search)
    })
  })

  const setVisibility = (isPublic) => {
    createForm.value.is_public = Boolean(isPublic)
  }

  const toggleVisibility = () => {
    setVisibility(!createForm.value.is_public)
  }

  const onVisibilityKeydown = (event) => {
    if (event.key === 'ArrowLeft') {
      event.preventDefault()
      setVisibility(false)
      return
    }

    if (event.key === 'ArrowRight') {
      event.preventDefault()
      setVisibility(true)
      return
    }

    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      toggleVisibility()
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
      showNotification('Unable to load profile information.', 'error')
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
      headers: createAuthHeaders(false),
    })

    if (response.status === 401) {
      redirectToLogin(router)
      return
    }

    if (!response.ok) {
      showNotification('Unable to load users list.', 'error')
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
      is_public: false,
      member_ids: [],
    }
  }

  const handleCreateTeam = async () => {
    createLoading.value = true
    hideNotification()

    try {
      const response = await fetch(`${API_BASE}/api/teams/`, {
        method: 'POST',
        headers: createAuthHeaders(true),
        body: JSON.stringify(createForm.value),
      })

      if (response.status === 401) {
        redirectToLogin(router)
        return
      }

      const data = await response.json()
      if (!response.ok) {
        showNotification(JSON.stringify(data), 'error')
        return
      }

      showNotification('Team created successfully.', 'success')
      resetCreateForm()
      router.push(`/teams/${data.id}`)
    } catch {
      showNotification('Server connection error.', 'error')
    } finally {
      createLoading.value = false
    }
  }

  onMounted(async () => {
    const ok = await fetchProfile()
    if (!ok) return
    await fetchUsers()
  })

  return {
    createCandidateUsers,
    createForm,
    createLoading,
    handleCreateTeam,
    memberSearch,
    onVisibilityKeydown,
    toggleVisibility,
  }
}
