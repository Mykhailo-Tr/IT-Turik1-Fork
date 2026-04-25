import type { AxiosError } from 'axios'
import type { MutationConfig } from '../types'
import type { ApiError } from '@/api'
import type { CreateTournamentArgs } from '@/api/tournaments/types'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import $api from '@/api'
import { touranmentsKeys } from '../keys'

export const useCreateTournament = (
  config?: MutationConfig<
    unknown,
    AxiosError<ApiError<keyof CreateTournamentArgs['body']>>,
    CreateTournamentArgs
  >,
) => {
  const queryClient = useQueryClient()
  return useMutation<
    unknown,
    AxiosError<ApiError<keyof CreateTournamentArgs['body']>>,
    CreateTournamentArgs
  >({
    mutationFn: $api.tournaments.createTournament,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: touranmentsKeys.allTouranments() })
    },
    ...config,
  })
}
