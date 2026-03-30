import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { API_BASE } from '@/features/shared/config/api'
import {
  createAuthHeaders,
  logoutToLogin as redirectToLogin,
} from '@/features/shared/lib/auth-session'
import { parseApiError } from '@/features/shared/lib/http-errors'
import { useGlobalNotification } from '@/features/shared/lib/notifications'

const PER_PAGE = 8

export const useTeamsViewPage = () => {
  const router = useRouter()
  const teams = ref([])
  const inboxInvitations = ref([])
  const currentUserId = ref(null)
  const loading = ref(true)
  const inboxLoading = ref(false)
  const invitationActionLoading = ref({})
  const joinRequestLoadingByTeam = ref({})
  const { showNotification, hideNotification } = useGlobalNotification()

  const myPage = ref(1)
  const otherPage = ref(1)

  const captainName = (team) => {
    const captain = team.members.find((member) => member.id === team.captain_id)
    return captain?.username || `User #${team.captain_id}`
  }

  const isCaptain = (team) => team.captain_id === currentUserId.value
  const isAcceptedMember = (team) => team.is_member || isCaptain(team)

  const myTeams = computed(() => teams.value.filter((team) => isAcceptedMember(team)))

  const otherTeams = computed(() => teams.value.filter((team) => !isAcceptedMember(team)))

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
      headers: createAuthHeaders(),
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

  const fetchTeams = async () => {
    const response = await fetch(`${API_BASE}/api/accounts/teams/`, {
      headers: createAuthHeaders(),
    })

    if (response.status === 401) {
      redirectToLogin(router)
      return
    }

    if (!response.ok) {
      showNotification('Unable to load teams.', 'error')
      return
    }

    teams.value = await response.json()
  }

  const fetchInvitations = async () => {
    inboxLoading.value = true
    try {
      const response = await fetch(`${API_BASE}/api/accounts/teams/invitations/`, {
        headers: createAuthHeaders(),
      })
      if (response.status === 401) {
        redirectToLogin(router)
        return
      }
      if (!response.ok) {
        showNotification(await parseApiError(response, 'Unable to load invitations.'), 'error')
        return
      }
      inboxInvitations.value = await response.json()
    } finally {
      inboxLoading.value = false
    }
  }

  const pendingInboxInvitations = computed(() =>
    inboxInvitations.value.filter((invitation) => invitation.status === 'invited'),
  )

  const respondToInvitation = async (invitationId, action) => {
    invitationActionLoading.value = {
      ...invitationActionLoading.value,
      [invitationId]: true,
    }
    hideNotification()
    try {
      const response = await fetch(
        `${API_BASE}/api/accounts/teams/invitations/${invitationId}/${action}/`,
        {
          method: 'POST',
          headers: createAuthHeaders(),
        },
      )
      if (response.status === 401) {
        redirectToLogin(router)
        return
      }
      if (!response.ok) {
        showNotification(await parseApiError(response, `Unable to ${action} invitation.`), 'error')
        return
      }
      showNotification(
        action === 'accept' ? 'Invitation accepted.' : 'Invitation declined.',
        'success',
      )
      await Promise.all([fetchTeams(), fetchInvitations()])
    } catch {
      showNotification('Server connection error.', 'error')
    } finally {
      invitationActionLoading.value = {
        ...invitationActionLoading.value,
        [invitationId]: false,
      }
    }
  }

  const sendJoinRequest = async (teamId) => {
    joinRequestLoadingByTeam.value = {
      ...joinRequestLoadingByTeam.value,
      [teamId]: true,
    }
    hideNotification()
    try {
      const response = await fetch(`${API_BASE}/api/accounts/teams/${teamId}/join-requests/`, {
        method: 'POST',
        headers: createAuthHeaders(),
      })
      if (response.status === 401) {
        redirectToLogin(router)
        return
      }
      if (!response.ok) {
        showNotification(await parseApiError(response, 'Unable to send join request.'), 'error')
        return
      }
      showNotification('Join request sent.', 'success')
      await fetchTeams()
    } catch {
      showNotification('Server connection error.', 'error')
    } finally {
      joinRequestLoadingByTeam.value = {
        ...joinRequestLoadingByTeam.value,
        [teamId]: false,
      }
    }
  }

  onMounted(async () => {
    const ok = await fetchProfile()
    if (!ok) {
      loading.value = false
      return
    }

    await fetchTeams()
    await fetchInvitations()
    loading.value = false
  })

  return {
    captainName,
    inboxLoading,
    invitationActionLoading,
    isCaptain,
    joinRequestLoadingByTeam,
    loading,
    myPage,
    myPages,
    myTeams,
    myTeamsPageItems,
    otherPage,
    otherPages,
    otherTeams,
    otherTeamsPageItems,
    pendingInboxInvitations,
    respondToInvitation,
    sendJoinRequest,
    teams,
  }
}
