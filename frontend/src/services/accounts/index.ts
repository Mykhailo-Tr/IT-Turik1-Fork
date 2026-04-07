import apiClient from '../apiClient'
import type { User } from '../dbTypes'
import type {
  ChangePasswordBody,
  CreateRoleCodesBody,
  ForgotPasswordBody,
  GenerateCodesResponse,
  GetProfileResponse,
  GetRoleCodesResponse,
  GetUsersResponse,
  GoogleLoginBody,
  LoginResponse,
  RegisterBody,
  RegisterResponse,
  ResetPasswordBody,
  ResetPasswordResponse,
  UpdateProfileBody,
  ValidatePasswordBody,
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

  async forgotPassword(data: ForgotPasswordBody) {
    return apiClient.post<ResetPasswordResponse>(`${prefix}/password-reset/`, {
      email: data.email,
    })
  },

  async resetPassword(data: ResetPasswordBody) {
    return apiClient.post<ResetPasswordResponse>(
      `${prefix}/password-reset/${data.info.uid}/${data.info.token}/`,
      data.body,
    )
  },

  async validatePassword(data: ValidatePasswordBody) {
    return apiClient.get<ResetPasswordResponse>(
      `${prefix}/password-reset/${data.info.uid}/${data.info.token}/`,
    )
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

  async googleLogin(body: GoogleLoginBody) {
    return apiClient.post(`${prefix}/google-login/`, body)
  },

  async register(data: RegisterBody) {
    return apiClient.post<RegisterResponse>(`${prefix}/register/`, data)
  },

  async getUsers() {
    return apiClient.get<GetUsersResponse>(`${prefix}/users`)
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
