import apiClient from '../apiClient'
import type { User } from '../dbTypes'
import type {
  ChangePasswordBody,
  CreateRoleCodesBody,
  CreateTeamBody,
  CreateTeamResponse,
  GenerateCodesResponse,
  GetProfileResponse,
  GetRoleCodesResponse,
  GetUsersResponse,
  LoginResponse,
  RegisterBody,
  RegisterResponse,
  ResetPasswordBody,
  ResetPasswordResponse,
  UpdateProfileBody,
} from './types'

const prefix = '/api/accounts'

export const accountsService = {
  async getProfile() {
    return apiClient.get<GetProfileResponse>(`${prefix}/profile`)
  },

  async deleteAccount() {
    return apiClient.delete(`${prefix}/profile/`)
  },

  async updateProfile(data: UpdateProfileBody) {
    return apiClient.patch(`${prefix}/profile/`, data)
  },

  // TODO: split into individual funcitons
  async resetPassword(data: ResetPasswordBody) {
    if (data.type === 'forgot')
      return apiClient.post<ResetPasswordResponse>(`${prefix}/password-reset/`, {
        email: data.email,
      })

    if (data.type === 'reset')
      return apiClient.post<ResetPasswordResponse>(
        `${prefix}/password-reset/${data.info.uid}/${data.info.token}/`,
        data.body,
      )

    if (data.type === 'validate') {
      return apiClient.get<ResetPasswordResponse>(
        `${prefix}/password-reset/${data.info.uid}/${data.info.token}/`,
      )
    }
  },

  async changePassword(data: ChangePasswordBody) {
    return apiClient.post(`${prefix}/change-password/`, data)
  },

  async login(data: { username: User['username']; password: string }) {
    return apiClient.post<LoginResponse>(`${prefix}/login/`, {
      username: data.username,
      password: data.password,
    })
  },

  async register(data: RegisterBody) {
    return apiClient.post<RegisterResponse>(`${prefix}/register/`, data)
  },

  async getUsers() {
    return apiClient.get<GetUsersResponse>(`${prefix}/users`)
  },

  // TODO: SPLIT ACCOUNTS TEAMS API TO ANOTHER SERVICE
  // shoud be base_url/teams not base_url/accounts/teams

  async createTeam(data: CreateTeamBody) {
    return apiClient.post<CreateTeamResponse>(`${prefix}/teams/`, data, {})
  },

  async getRoleCodes(filter?: { role?: User['role'] | 'all' }) {
    const params = new URLSearchParams()

    if (filter?.role && filter.role !== 'all') {
      params.append('role', String(filter.role))
    }

    return apiClient.get<GetRoleCodesResponse>(`${prefix}/role-codes`, {
      params,
    })
  },

  async generateCodes(data: CreateRoleCodesBody) {
    return apiClient.post<GenerateCodesResponse>(`${prefix}/role-codes/`, data)
  },
}
