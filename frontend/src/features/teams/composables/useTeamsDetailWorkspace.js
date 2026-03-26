import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { API_BASE } from '@/features/shared/config/api'
import { createAuthHeaders, logoutToLogin as redirectToLogin } from '@/features/shared/lib/auth-session'
import { parseApiError } from '@/features/shared/lib/http-errors'
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import { discordLink, telegramLink } from '@/features/teams/lib/team-links'

export const useTeamsDetailWorkspace = () => {
  const route = useRoute()
  const router = useRouter()

  const team = ref(null)
  const currentUserId = ref(null)

  const loading = ref(true)
  const loadError = ref('')
  const { showNotification, hideNotification } = useGlobalNotification()

  const memberSearch = ref('')
  const isLeaveModalOpen = ref(false)
  const isDeleteModalOpen = ref(false)
  const isVisibilityModalOpen = ref(false)
  const selectedVisibility = ref(null)
  const visibilityLoading = ref(false)
  const visibilityError = ref('')
  const deleteConfirmInput = ref('')
  const deleteTeamLoading = ref(false)
  const deleteError = ref('')
  const joinRequestLoading = ref(false)
  const leaveTeamLoading = ref(false)
  const joinRequestActionLoading = ref({})
  const resendInvitationLoading = ref({})

  const teamId = computed(() => Number(route.params.id))
  const isCaptain = computed(() => Boolean(team.value) && team.value.captain_id === currentUserId.value)
  const canLeaveTeam = computed(() => Boolean(team.value?.is_member) && !isCaptain.value)

  const captainName = computed(() => {
    if (!team.value) return '-'
    const captain = team.value.members.find((member) => member.id === team.value.captain_id)
    return captain?.username || `User #${team.value.captain_id}`
  })

  const filteredMembers = computed(() => {
    if (!team.value) return []
    const search = memberSearch.value.trim().toLowerCase()
    if (!search) return team.value.members

    return team.value.members.filter((member) => {
      return [member.username, member.email, member.full_name || ''].join(' ').toLowerCase().includes(search)
    })
  })

  const pendingJoinRequests = computed(() => {
    if (!team.value?.join_requests) return []
    return team.value.join_requests.filter((item) => item.status === 'pending')
  })

  const filteredPendingJoinRequests = computed(() => {
    if (!team.value) return []
    const list = pendingJoinRequests.value
    const search = memberSearch.value.trim().toLowerCase()
    if (!search) return list
    return list.filter((jr) => {
      const text = [jr.user.username, jr.user.email, jr.user.full_name || ''].join(' ').toLowerCase()
      return text.includes(search)
    })
  })

  const uniqueInvitations = computed(() => {
    if (!team.value?.invitations) return []
    const byUserId = new Map()
    for (const invitation of team.value.invitations) {
      const userId = invitation?.user?.id
      if (!userId) continue
      if (!byUserId.has(userId)) {
        byUserId.set(userId, invitation)
        continue
      }
      const prev = byUserId.get(userId)
      const prevTime = new Date(prev.created_at || 0).getTime()
      const nextTime = new Date(invitation.created_at || 0).getTime()
      if (nextTime >= prevTime) byUserId.set(userId, invitation)
    }
    return Array.from(byUserId.values())
  })

  const pendingInvitations = computed(() => uniqueInvitations.value.filter((invitation) => invitation.status === 'invited'))
  const declinedInvitations = computed(() => uniqueInvitations.value.filter((invitation) => invitation.status === 'declined'))

  const filteredPendingInvitations = computed(() => {
    if (!team.value) return []
    const list = pendingInvitations.value
    const search = memberSearch.value.trim().toLowerCase()
    if (!search) return list
    return list.filter((inv) => {
      const text = [inv.user.username, inv.user.email, inv.user.full_name || ''].join(' ').toLowerCase()
      return text.includes(search)
    })
  })

  const filteredDeclinedInvitations = computed(() => {
    if (!team.value) return []
    const list = declinedInvitations.value
    const search = memberSearch.value.trim().toLowerCase()
    if (!search) return list
    return list.filter((inv) => {
      const text = [inv.user.username, inv.user.email, inv.user.full_name || ''].join(' ').toLowerCase()
      return text.includes(search)
    })
  })

  const statusByUserId = computed(() => {
    const map = {}
    if (!team.value) return map

    const membersSet = new Set((team.value.members || []).map((m) => m.id))
    const myInvitationStatus = team.value.my_invitation_status
    const myJoinRequestStatus = team.value.my_join_request_status
    const invitations = team.value.invitations || []
    const joinRequests = team.value.join_requests || []

    const invitationByUserId = {}
    for (const inv of invitations) {
      const uid = inv?.user?.id
      if (uid) invitationByUserId[uid] = inv
    }

    const joinRequestByUserId = {}
    for (const jr of joinRequests) {
      const uid = jr?.user?.id
      if (uid) joinRequestByUserId[uid] = jr
    }

    const allUserIds = new Set([
      ...membersSet,
      ...Object.keys(invitationByUserId).map((x) => Number(x)),
      ...Object.keys(joinRequestByUserId).map((x) => Number(x)),
    ])

    for (const userId of allUserIds) {
      const invitation = invitationByUserId[userId]
      const joinRequest = joinRequestByUserId[userId]
      const accepted = membersSet.has(userId)
      const isCurrentUser = userId === currentUserId.value

      const invitationStatus = invitation?.status ?? (isCurrentUser ? myInvitationStatus : null)
      const joinRequestStatus = joinRequest?.status ?? (isCurrentUser ? myJoinRequestStatus : null)

      const invited = invitationStatus === 'invited'
      const pending = joinRequestStatus === 'pending'
      const declined = invitationStatus === 'declined' || joinRequestStatus === 'declined'

      let source = 'Member'
      if (accepted) {
        if (joinRequestStatus === 'accepted') source = 'Join request'
        else if (invitationStatus === 'accepted') source = 'Invitation'
        else if (joinRequestStatus) source = 'Join request'
        else if (invitationStatus) source = 'Invitation'
      } else if (invitationStatus) source = 'Invitation'
      else if (joinRequestStatus) source = 'Join request'

      map[userId] = { accepted, declined, invited, pending, source }
    }

    return map
  })

  const expectedDeleteText = computed(() => team.value?.name || '')
  const canDeleteTeam = computed(() => {
    return Boolean(expectedDeleteText.value) && deleteConfirmInput.value === expectedDeleteText.value && !deleteTeamLoading.value
  })

  const logoutToLogin = () => {
    redirectToLogin(router)
  }

  const fetchProfile = async () => {
    const response = await fetch(`${API_BASE}/api/accounts/profile/`, {
      headers: createAuthHeaders(false),
    })

    if (response.status === 401) {
      logoutToLogin()
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

    const response = await fetch(`${API_BASE}/api/accounts/teams/${teamId.value}/`, {
      headers: createAuthHeaders(false),
    })

    if (response.status === 401) {
      logoutToLogin()
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
    return true
  }

  const loadWorkspace = async () => {
    loading.value = true
    loadError.value = ''
    isLeaveModalOpen.value = false
    isDeleteModalOpen.value = false
    deleteConfirmInput.value = ''
    deleteError.value = ''

    const profileOk = await fetchProfile()
    if (!profileOk) {
      loading.value = false
      return
    }

    await fetchTeam()
    loading.value = false
  }

  const openVisibilityModal = () => {
    selectedVisibility.value = team.value?.is_public ?? true
    visibilityError.value = ''
    isVisibilityModalOpen.value = true
  }

  const closeVisibilityModal = () => {
    if (visibilityLoading.value) return
    isVisibilityModalOpen.value = false
  }

  const confirmChangeVisibility = async () => {
    if (!team.value || !isCaptain.value) return
    if (selectedVisibility.value === team.value.is_public) return

    visibilityLoading.value = true
    visibilityError.value = ''
    hideNotification()

    try {
      const response = await fetch(`${API_BASE}/api/accounts/teams/${team.value.id}/`, {
        method: 'PATCH',
        headers: createAuthHeaders(true),
        body: JSON.stringify({ is_public: selectedVisibility.value }),
      })

      if (response.status === 401) {
        logoutToLogin()
        return
      }

      if (!response.ok) {
        visibilityError.value = await parseApiError(response, 'Unable to change team visibility.')
        return
      }

      team.value = await response.json()
      isVisibilityModalOpen.value = false
      showNotification(`Team visibility changed to ${team.value.is_public ? 'Public' : 'Private'}.`, 'success')
    } catch {
      visibilityError.value = 'Server connection error.'
    } finally {
      visibilityLoading.value = false
    }
  }

  const openDeleteModal = () => {
    deleteConfirmInput.value = ''
    deleteError.value = ''
    isDeleteModalOpen.value = true
  }

  const closeDeleteModal = () => {
    if (deleteTeamLoading.value) return
    isDeleteModalOpen.value = false
  }

  const confirmDeleteTeam = async () => {
    if (!team.value) return
    if (!canDeleteTeam.value) {
      deleteError.value = `Please enter "${expectedDeleteText.value}" exactly.`
      return
    }

    deleteTeamLoading.value = true
    deleteError.value = ''
    hideNotification()
    try {
      const response = await fetch(`${API_BASE}/api/accounts/teams/${team.value.id}/`, {
        method: 'DELETE',
        headers: createAuthHeaders(false),
      })

      if (response.status === 401) {
        logoutToLogin()
        return
      }

      if (!response.ok && response.status !== 204) {
        deleteError.value = await parseApiError(response, 'Unable to delete team.')
        return
      }

      router.push('/teams')
    } catch {
      deleteError.value = 'Server connection error.'
    } finally {
      deleteTeamLoading.value = false
    }
  }

  const sendJoinRequest = async () => {
    if (!team.value) return
    joinRequestLoading.value = true
    hideNotification()
    try {
      const response = await fetch(`${API_BASE}/api/accounts/teams/${team.value.id}/join-requests/`, {
        method: 'POST',
        headers: createAuthHeaders(false),
      })
      if (response.status === 401) {
        logoutToLogin()
        return
      }
      if (!response.ok) {
        showNotification(await parseApiError(response, 'Unable to send join request.'), 'error')
        return
      }
      showNotification('Join request sent.', 'success')
      await fetchTeam()
    } catch {
      showNotification('Server connection error.', 'error')
    } finally {
      joinRequestLoading.value = false
    }
  }

  const openLeaveModal = () => {
    if (!canLeaveTeam.value || leaveTeamLoading.value) return
    isLeaveModalOpen.value = true
  }

  const closeLeaveModal = () => {
    if (leaveTeamLoading.value) return
    isLeaveModalOpen.value = false
  }

  const confirmLeaveTeam = async () => {
    if (!team.value || !canLeaveTeam.value || leaveTeamLoading.value) return
    await leaveTeam()
  }

  const leaveTeam = async () => {
    if (!team.value || !canLeaveTeam.value) return

    leaveTeamLoading.value = true
    hideNotification()

    try {
      const response = await fetch(`${API_BASE}/api/accounts/teams/${team.value.id}/leave/`, {
        method: 'POST',
        headers: createAuthHeaders(false),
      })
      if (response.status === 401) {
        logoutToLogin()
        return
      }
      if (!response.ok) {
        showNotification(await parseApiError(response, 'Unable to leave team.'), 'error')
        return
      }

      team.value = {
        ...team.value,
        members: (team.value.members || []).filter((member) => member.id !== currentUserId.value),
        invitations: (team.value.invitations || []).filter((inv) => inv.user?.id !== currentUserId.value),
        join_requests: (team.value.join_requests || []).filter((jr) => jr.user?.id !== currentUserId.value),
        my_invitation_status: null,
        my_join_request_status: null,
        is_member: false,
        can_request_to_join: Boolean(team.value.is_public),
      }
      isLeaveModalOpen.value = false
      showNotification('You left the team.', 'success')

      if (!team.value.is_public) {
        router.push('/teams')
        return
      }

      await fetchTeam()
    } catch {
      showNotification('Server connection error.', 'error')
    } finally {
      leaveTeamLoading.value = false
    }
  }

  const reviewJoinRequest = async (requestId, action) => {
    if (!team.value || !isCaptain.value) return
    joinRequestActionLoading.value = {
      ...joinRequestActionLoading.value,
      [requestId]: true,
    }
    hideNotification()
    try {
      const response = await fetch(`${API_BASE}/api/accounts/teams/${team.value.id}/join-requests/${requestId}/${action}/`, {
        method: 'POST',
        headers: createAuthHeaders(false),
      })
      if (response.status === 401) {
        logoutToLogin()
        return
      }
      if (!response.ok) {
        showNotification(await parseApiError(response, `Unable to ${action} join request.`), 'error')
        return
      }
      showNotification(`Join request ${action}ed.`, 'success')
      team.value = await response.json()
    } catch {
      showNotification('Server connection error.', 'error')
    } finally {
      joinRequestActionLoading.value = {
        ...joinRequestActionLoading.value,
        [requestId]: false,
      }
    }
  }

  const resendInvitation = async (userId) => {
    if (!team.value || !isCaptain.value) return
    resendInvitationLoading.value = {
      ...resendInvitationLoading.value,
      [userId]: true,
    }
    hideNotification()

    try {
      const response = await fetch(`${API_BASE}/api/accounts/teams/${team.value.id}/members/`, {
        method: 'POST',
        headers: createAuthHeaders(true),
        body: JSON.stringify({ user_id: userId }),
      })

      if (response.status === 401) {
        logoutToLogin()
        return
      }

      if (!response.ok) {
        showNotification(await parseApiError(response, 'Unable to resend invitation.'), 'error')
        return
      }

      team.value = await response.json()
      showNotification('Invitation resent.', 'success')
    } catch {
      showNotification('Server connection error.', 'error')
    } finally {
      resendInvitationLoading.value = {
        ...resendInvitationLoading.value,
        [userId]: false,
      }
    }
  }

  onMounted(loadWorkspace)

  watch(
    () => route.params.id,
    () => {
      loadWorkspace()
    },
  )

  return {
    canDeleteTeam,
    canLeaveTeam,
    captainName,
    closeDeleteModal,
    closeLeaveModal,
    closeVisibilityModal,
    confirmChangeVisibility,
    confirmDeleteTeam,
    confirmLeaveTeam,
    deleteConfirmInput,
    deleteError,
    deleteTeamLoading,
    discordLink,
    expectedDeleteText,
    filteredDeclinedInvitations,
    filteredMembers,
    filteredPendingInvitations,
    filteredPendingJoinRequests,
    isCaptain,
    isDeleteModalOpen,
    isLeaveModalOpen,
    isVisibilityModalOpen,
    joinRequestActionLoading,
    joinRequestLoading,
    leaveTeamLoading,
    loadError,
    loading,
    memberSearch,
    openDeleteModal,
    openLeaveModal,
    openVisibilityModal,
    resendInvitation,
    resendInvitationLoading,
    reviewJoinRequest,
    selectedVisibility,
    sendJoinRequest,
    statusByUserId,
    team,
    telegramLink,
    visibilityError,
    visibilityLoading,
  }
}

