import { apiClient } from '../apiClient'
import type { CreateTournamentArgs } from './types'

const prefix = '/api/tournaments'

export const tournamentsService = {
  createTournament: async (args: CreateTournamentArgs) => {
    const { data } = await apiClient.post(`${prefix}/manage/`, args.body)
    return data
  },
}
