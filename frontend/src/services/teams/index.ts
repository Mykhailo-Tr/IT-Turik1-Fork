import apiClient from '../apiClient'
import type { Invitation, InvitationId, JoinRequestId, Team, TeamId, UserId } from '../dbTypes'
import type {
  AddMemberBody,
  ChangeTeamVisibilityBody,
  CreateTeamBody,
  CreateTeamResponse,
  GetTeamInfoResponse,
  GetTeamsResponse,
  ManageJoinRequestAction,
  ResendInvatationBody,
  UpdateTeamInfoBody,
} from './types'

// TODO: change to /api/teams
const prefix = '/api/accounts/teams'

export const teamsService = {
  async createTeam(data: CreateTeamBody) {
    return apiClient.post<CreateTeamResponse>(`${prefix}/teams/`, data, {})
  },

  getTeamInfo(id: TeamId) {
    return apiClient.get<GetTeamInfoResponse>(`${prefix}/${id}`)
  },

  getTeams() {
    return apiClient.get<GetTeamsResponse[]>(`${prefix}/`)
  },

  getInvatations() {
    return apiClient.get<Invitation[]>(`${prefix}/invitations/`)
  },

  respondToInvitation(invitationId: InvitationId, action: 'accept' | 'decline') {
    return apiClient.post(`${prefix}/invitations/${invitationId}/${action}/`)
  },

  sendJoinRequest(id: TeamId) {
    return apiClient.post(`${prefix}/${id}/join-requests/`)
  },

  deleteTeam(id: TeamId) {
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

  updateInfo(teamId: TeamId, body: UpdateTeamInfoBody) {
    return apiClient.patch(`${prefix}/${teamId}/`, body)
  },

  removeMember(teamId: TeamId, memberId: UserId) {
    return apiClient.delete(`${prefix}/${teamId}/members/${memberId}/`)
  },

  addMember(teamId: TeamId, body: AddMemberBody) {
    return apiClient.post(`${prefix}/${teamId}/members/`)
  },
}
