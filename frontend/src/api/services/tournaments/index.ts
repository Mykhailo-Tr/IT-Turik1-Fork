import { apiClient } from '@/api/client'
import type {
  CreateRoundArgs,
  CreateTournamentArgs,
  GetCurrentRoundArgs,
  GetCurrentRoundResponse,
  GetEligibleTeamsArgs,
  GetEligibleTeamsResponse,
  GetRegisteredTeamsArgs,
  GetRegisteredTeamsResponse,
  GetRoundsArgs,
  GetRoundsResponse,
  GetTournamentInfoArgs,
  GetTournamentInfoResponse,
  GetTournamentsArgs,
  RegisterTeamArgs,
} from './types'

const prefix = '/api/tournaments'

export const tournamentsService = {
  getTournaments: async (args: GetTournamentsArgs) => {
    const params = new URLSearchParams()

    if (args.page) {
      params.append('page', String(args.page))
    }
    if (args.pageSize) {
      params.append('pageSize', String(args.pageSize))
    }
    if (args.searchQuery) {
      params.append('searchQuery', args.searchQuery)
    }
    if (args.status) {
      params.append('status', args.status.join(','))
    }

    const { data } = await apiClient.get(`${prefix}?${params.toString()}`)
    return data
  },

  getRegisteredTeams: async (args: GetRegisteredTeamsArgs) => {
    const { data } = await apiClient.get<GetRegisteredTeamsResponse>(`${prefix}/${args.id}/teams`)
    return data
  },

  getRounds: async (args: GetRoundsArgs) => {
    const { data } = await apiClient.get<GetRoundsResponse>(`${prefix}/${args.id}/rounds`)
    return data
  },

  createTournament: async (args: CreateTournamentArgs) => {
    const { data } = await apiClient.post(`${prefix}/manage/`, args.body)
    return data
  },

  getTournamentInfo: async (args: GetTournamentInfoArgs) => {
    const { data } = await apiClient.get<GetTournamentInfoResponse>(`${prefix}/${args.id}`)
    return data
  },

  getEligibleTeams: async (args: GetEligibleTeamsArgs) => {
    const { data } = await apiClient.get<GetEligibleTeamsResponse>(
      `${prefix}/${args.id}/eligible-teams`,
    )
    return data
  },

  createRound: async (args: CreateRoundArgs) => {
    const { data } = await apiClient.post(`${prefix}/${args.id}/rounds/`, args.body)
    return data
  },

  getCurrentRound: async (args: GetCurrentRoundArgs) => {
    const { data } = await apiClient.get<GetCurrentRoundResponse>(
      `${prefix}/current-task/?tournament_id=${args.id}`,
    )
    return data
  },

  registerTeam: async (args: RegisterTeamArgs) => {
    const { data } = await apiClient.post(`${prefix}/${args.id}/register-team/`, args.body)
    return data
  },
}
