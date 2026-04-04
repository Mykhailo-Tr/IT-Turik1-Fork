import apiClient from '../apiClient'
import type { JoinRequestId, TeamId } from '../dbTypes'
import type {
  ChangeTeamVisibilityBody,
  GetTeamInfoResponse,
  ManageJoinRequestAction,
  ResendInvatationBody,
} from './types'

// TODO: change to /api/teams
const prefix = '/api/accounts/teams'

export const teamsService = {
  getTeamInfo(id: TeamId) {
    return apiClient.get<GetTeamInfoResponse>(`${prefix}/${id}`)
  },

  sendJoinRequest(id: TeamId) {
    return apiClient.post(`${prefix}/${id}/join-requests/`)
  },

  deleteTeam(id: TeamId) {
    // TODO: asd
    return apiClient.delete(`${prefix}/${id}/`)
  },

  leave(id: TeamId) {
    return apiClient.post(`${prefix}/${id}/leave/`)
  },

  manageJoinRequest(id: JoinRequestId, teamId: TeamId, action: ManageJoinRequestAction) {
    return apiClient.post<GetTeamInfoResponse>(`${prefix}/${teamId}/join-requests/${id}/${action}/`)
  },

  resendInvatation(teamId: TeamId, body: ResendInvatationBody) {
    return apiClient.post<GetTeamInfoResponse>(`${prefix}/${teamId}/members/`, body)
  },

  changeTeamVisibility(teamId: TeamId, body: ChangeTeamVisibilityBody) {
    return apiClient.patch<GetTeamInfoResponse>(`${prefix}/${teamId}/`, body)
  },
}
