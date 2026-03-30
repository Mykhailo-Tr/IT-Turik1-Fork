import apiClient from '../apiClient'

const prefix = '/api/accounts'

// TODO: split types of db into separate files
// then use here with Pick<> Omit<> and other Ts helper types

export interface Profile {
  id: number
  username: string
  email: string
  role: 'admin' | 'team' | 'jury' | 'organizer'
  full_name: string
  phone: string
  city: string
  created_at: Date
  needs_onboarding: boolean
  teams: Team[]
}

interface Team {
  id: number
  name: string
  contact_telegram: string
  contact_discord: string
}

type UpdateProfileBody = Partial<
  Pick<Profile, 'username' | 'role' | 'full_name' | 'phone' | 'city'>
> & {
  redeem_code?: string
  password?: string
}

interface ResetPasswordResponse {
  message: string
}

interface ChangePasswordBody {
  current_password: string
  new_password: string
  confirm_password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  onboarding_required: boolean
}

interface RegisterBody {
  username: string
  email: string
  password: string
  role: string
  redeem_code: string
  full_name: string
  phone: string
  city: string
}

export interface RegisterResponse {
  access: string
  refresh: string
  onboarding_required: boolean
}

type ResetPasswordBody =
  | { type: 'forgot'; email: string }
  | {
      type: 'reset'
      info: { uid: string; token: string }
      body: { new_password: string; confirm_password: string }
    }
  | {
      type: 'validate'
      info: { uid: string; token: string }
    }

export type GetUsersResponse = Pick<Profile, 'id' | 'username' | 'email' | 'full_name' | 'role'>[]

interface CreateTeamBody {
  name: string
  email: string
  organization: string
  contact_telegram: string
  contact_discord: string
  is_public: boolean
  member_ids: never[]
}

interface Invatation {
  id: number
  user: Pick<Profile, 'id' | 'username' | 'email' | 'full_name' | 'role'>
  status: string
  created_at: Date
  responded_at: Date
  invited_by_id: number
}

interface CreateTeamResponse {
  id: number
  name: string
  email: string
  captain_id: number
  is_public: boolean
  organization: string
  contact_telegram: string
  contact_discord: string
  members: Pick<Profile, 'id' | 'username' | 'email' | 'full_name' | 'role'>[]
  invitations: Invatation[]
  join_requests: [] // TODO: add type annotation
  my_invitation_status: boolean
  my_join_request_status: boolean
  is_member: boolean
  is_captain: boolean
  can_request_to_join: boolean
}

export type RoleCode =
  | {
      id: number
      code: string
      role: Profile['role']
      is_used: true
      created_at: Date
      used_at: Date
      used_by: string
      created_by_username: string
    }
  | {
      id: number
      code: string
      role: Profile['role']
      is_used: false
      created_at: Date
      used_at: Date
      created_by_username: string
    }

export type RoleCodesUserRole = Extract<Profile['role'], 'admin' | 'jury' | 'organizer'>

type GetRoleCodesResponse = {
  codes: RoleCode[]
  active_counts: Record<RoleCodesUserRole, number>
}

interface CreateRoleCodesBody {
  role: string
  quantity: number
}

type GenerateCodesResponse = Pick<GetRoleCodesResponse, 'active_counts'> & {
  created: RoleCode[]
}

export const accountsService = {
  async getProfile(token: string) {
    return apiClient.get<Profile>(`${prefix}/profile`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async updateProfile(token: string, data: UpdateProfileBody) {
    return apiClient.patch(`${prefix}/profile/`, data, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
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

  async changePassword(token: string, data: ChangePasswordBody) {
    return apiClient.post(`${prefix}/change-password/`, data, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async login(username: string, password: string) {
    return apiClient.post<LoginResponse>(`${prefix}/login/`, { username, password })
  },

  async register(data: RegisterBody) {
    return apiClient.post<RegisterResponse>(`${prefix}/register/`, data)
  },

  async getUsers(token: string) {
    return apiClient.get<GetUsersResponse>(`${prefix}/users`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  // TODO: SPLIT ACCOUNTS TEAMS API TO ANOTHER SERVICE
  // shoud be base_url/teams not base_url/accounts/teams

  async createTeam(token: string, data: CreateTeamBody) {
    return apiClient.post<CreateTeamResponse>(`${prefix}/teams/`, data, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async getRoleCodes(token: string, filter?: { role?: Profile['role'] | 'all' }) {
    const params = new URLSearchParams()

    if (filter?.role && filter.role !== 'all') {
      params.append('role', String(filter.role))
    }

    return apiClient.get<GetRoleCodesResponse>(`${prefix}/role-codes`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      params,
    })
  },

  async generateCodes(token: string, data: CreateRoleCodesBody) {
    return apiClient.post<GenerateCodesResponse>(`${prefix}/role-codes/`, data, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },
}
