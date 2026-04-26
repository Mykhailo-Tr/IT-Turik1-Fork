import { apiClient } from '@/api'
import type {
  CreateRoundArgs,
  CreateTournamentArgs,
  GetTournamentInfoArgs,
  GetTournamentInfoResponse,
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

  createRound: async (args: CreateRoundArgs) => {
    const { data } = await apiClient.post(`${prefix}/rounds/`, args.body)
    return data
  },
}
