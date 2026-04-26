import type { AxiosError } from 'axios'
import type { MutationConfig, QueryConfig } from '../types'
import type {
  CreateRoundArgs,
  CreateTournamentArgs,
  GetCurrentRoundArgs,
  GetCurrentRoundResponse,
  GetEligibleTeamsArgs,
  GetEligibleTeamsResponse,
  GetTournamentInfoArgs,
  GetTournamentInfoResponse,
  RegisterTeamArgs,
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

export const useEligibleTeams = (
  payload: GetEligibleTeamsArgs,
  config?: QueryConfig<GetEligibleTeamsResponse>,
) => {
  return useQuery<GetEligibleTeamsResponse, AxiosError<ApiError>>({
    queryKey: touranmentsKeys['eligible-teams'](),
    queryFn: () => $api.tournaments.getEligibleTeams({ id: payload.id }),
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
  const _queryClient = useQueryClient()
  return useMutation<unknown, AxiosError<ApiError<keyof CreateRoundArgs['body']>>, CreateRoundArgs>(
    {
      mutationFn: $api.tournaments.createRound,
      onSuccess: () => {
        // TODO:
        // queryClient.invalidateQueries({ queryKey: touranmentsKeys.allTouranments() })
      },
      ...config,
    },
  )
}

export const useCurrentRound = (
  payload: GetCurrentRoundArgs,
  config?: QueryConfig<GetCurrentRoundResponse>,
) => {
  return useQuery<GetCurrentRoundResponse, AxiosError<ApiError>>({
    queryKey: touranmentsKeys['current-round'](payload.id),
    queryFn: () => $api.tournaments.getCurrentRound({ id: payload.id }),
    ...config,
  })
}

export const useRegisterTeam = (
  config?: MutationConfig<
    unknown,
    AxiosError<ApiError<keyof RegisterTeamArgs['body']>>,
    RegisterTeamArgs
  >,
) => {
  const queryClient = useQueryClient()
  return useMutation<
    unknown,
    AxiosError<ApiError<keyof RegisterTeamArgs['body']>>,
    RegisterTeamArgs
  >({
    mutationFn: $api.tournaments.registerTeam,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: touranmentsKeys['eligible-teams']() })
    },
    ...config,
  })
}
