import $api from '@/api'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { teamKeys } from '../keys'
import type { AxiosError } from 'axios'
import type { TeamId } from '@/api/dbTypes'
import type {
  AddMemberArgs,
  ChangeTeamVisibilityArgs,
  ChangeTeamVisibilityResponse,
  DeleteTeamArgs,
  GetTeamInfoResponse,
  GetTeamsResponse,
  LeaveTeamArgs,
  ManageJoinRequestArgs,
  RemoveMemberArgs,
  ResendInvitationArgs,
  RespondToInvitationArgs,
  SendJoinRequestArgs,
  UpdateTeamInfoArgs,
} from '@/api/teams/types'

export const useTeams = () => {
  return useQuery<GetTeamsResponse, AxiosError>({
    queryKey: teamKeys.allTeams(),
    queryFn: $api.teams.getTeams,
  })
}

export const useTeamInfo = (id: TeamId) => {
  return useQuery<GetTeamInfoResponse, AxiosError>({
    queryKey: teamKeys.team(id),
    queryFn: () => $api.teams.getTeamInfo({ id }),
  })
}

export const useInvitations = () => {
  return useQuery({
    queryKey: ['invitations'],
    queryFn: $api.teams.getInvitations,
  })
}

export const useCreateTeam = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: $api.teams.createTeam,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: teamKeys.allTeams() })
    },
  })
}

export const useRespondToInvitation = () => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError, RespondToInvitationArgs>({
    mutationFn: $api.teams.respondToInvitation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invitations'] })
      queryClient.invalidateQueries({ queryKey: teamKeys.allTeams() })
    },
  })
}

export const useSendJoinRequest = () => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError, SendJoinRequestArgs>({
    mutationFn: $api.teams.sendJoinRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: teamKeys.allTeams() })
    },
  })
}

export const useDeleteTeam = () => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError, DeleteTeamArgs>({
    mutationFn: $api.teams.deleteTeam,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: teamKeys.allTeams() })
    },
  })
}

export const useLeaveTeam = () => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError, LeaveTeamArgs>({
    mutationFn: $api.teams.leave,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: teamKeys.allTeams() })
    },
  })
}

export const useManageJoinRequest = () => {
  const queryClient = useQueryClient()
  return useMutation<GetTeamInfoResponse, AxiosError, ManageJoinRequestArgs>({
    mutationFn: $api.teams.manageJoinRequest,
    onSuccess: (_, { teamId }) => {
      queryClient.invalidateQueries({ queryKey: teamKeys.team(teamId) })
    },
  })
}

export const useResendInvitation = () => {
  const queryClient = useQueryClient()
  return useMutation<GetTeamInfoResponse, AxiosError, ResendInvitationArgs>({
    mutationFn: $api.teams.resendInvitation,
    onSuccess: (_, { teamId }) => {
      queryClient.invalidateQueries({ queryKey: teamKeys.team(teamId) })
    },
  })
}

export const useChangeTeamVisibility = () => {
  const queryClient = useQueryClient()
  return useMutation<ChangeTeamVisibilityResponse, AxiosError, ChangeTeamVisibilityArgs>({
    mutationFn: $api.teams.changeTeamVisibility,
    onSuccess: (_, { teamId }) => {
      queryClient.invalidateQueries({ queryKey: teamKeys.team(teamId) })
    },
  })
}

export const useUpdateTeamInfo = () => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError, UpdateTeamInfoArgs>({
    mutationFn: $api.teams.updateInfo,
    onSuccess: (_, { teamId }) => {
      queryClient.invalidateQueries({ queryKey: teamKeys.team(teamId) })
    },
  })
}

export const useRemoveMember = () => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError, RemoveMemberArgs>({
    mutationFn: $api.teams.removeMember,
    onSuccess: (_, { teamId }) => {
      queryClient.invalidateQueries({ queryKey: teamKeys.team(teamId) })
    },
  })
}

export const useAddMember = () => {
  const queryClient = useQueryClient()
  return useMutation<unknown, AxiosError, AddMemberArgs>({
    mutationFn: $api.teams.addMember,
    onSuccess: (_, { teamId }) => {
      queryClient.invalidateQueries({ queryKey: teamKeys.team(teamId) })
    },
  })
}
