import { apiClient } from '@/api'
import type { CreateRoundArgs, CreateTournamentArgs } from './types'

const prefix = '/api/tournaments'

export const tournamentsService = {
  createTournament: async (args: CreateTournamentArgs) => {
    const { data } = await apiClient.post(`${prefix}/manage/`, args.body)
    return data
  },

  createRound: async (args: CreateRoundArgs) => {
    const { data } = await apiClient.post(`${prefix}/rounds/`, args.body)
    return data
  },
}
