import { apiClient } from '@/api'
import type {
  CreateRoundArgs,
  CreateTournamentArgs,
  GetCurrentRoundArgs,
  GetCurrentRoundResponse,
  GetEligibleTeamsArgs,
  GetTournamentInfoArgs,
  GetTournamentInfoResponse,
  RegisterTeamArgs,
} from './types'

const prefix = '/api/tournaments'

export const tournamentsService = {
  createTournament: async (args: CreateTournamentArgs) => {
    const { data } = await apiClient.post(`${prefix}/manage/`, args.body)
    return data
  },

  getTournamentInfo: async (args: GetTournamentInfoArgs) => {
    const { data } = await apiClient.get<GetTournamentInfoResponse>(`${prefix}/${args.id}`)
    return data
  },

  getEligibleTeams: async (args: GetEligibleTeamsArgs) => {
    const { data } = await apiClient.get(`${prefix}/${args.id}/eligible-teams`)
    return data
  },

  createRound: async (args: CreateRoundArgs) => {
    const { data } = await apiClient.post(`${prefix}/rounds/`, args.body)
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
