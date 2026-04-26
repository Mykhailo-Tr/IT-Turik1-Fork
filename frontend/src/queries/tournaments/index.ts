import type { AxiosError } from 'axios'
import type { MutationConfig, QueryConfig } from '../types'
import type {
  CreateRoundArgs,
  CreateTournamentArgs,
  GetTournamentInfoArgs,
  GetTournamentInfoResponse,
} from '@/api/services/tournaments/types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { $api, type ApiError } from '@/api'
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

export const useTournamentInfo = (
  payload: GetTournamentInfoArgs,
  config?: QueryConfig<GetTournamentInfoResponse>,
) => {
  return useQuery<GetTournamentInfoResponse, AxiosError<ApiError>>({
    queryKey: touranmentsKeys.touranment(payload.id),
    queryFn: () => $api.tournaments.getTournamentInfo({ id: payload.id }),
    ...config,
  })
}

export const useCreateRound = (
  config?: MutationConfig<
    unknown,
    AxiosError<ApiError<keyof CreateRoundArgs['body']>>,
    CreateRoundArgs
  >,
) => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError<keyof CreateRoundArgs['body']>>, CreateRoundArgs>(
    {
      mutationFn: $api.tournaments.createRound,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: touranmentsKeys.allTouranments() })
      },
      ...config,
    },
  )
}
