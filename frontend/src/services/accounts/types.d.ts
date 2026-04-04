import type { Invatation, Team, User, UserId } from '../dbTypes'

export type GetProfileResponse = User & {
  teams: Pick<Team, 'id' | 'name' | 'contact_discord' | 'contact_telegram'>[]
}

type UpdateProfileBody = Partial<User>

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

export type GetUsersResponse = Pick<User, 'id' | 'username' | 'email' | 'full_name' | 'role'>[]

interface CreateTeamBody {
  name: string
  email: string
  organization: string
  contact_telegram: string
  contact_discord: string
  is_public: boolean
  member_ids: UserId[]
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
  members: Pick<User, 'id' | 'username' | 'email' | 'full_name' | 'role'>[]
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
      role: User['role']
      is_used: true
      created_at: Date
      used_at: Date
      used_by: string
      created_by_username: string
    }
  | {
      id: number
      code: string
      role: User['role']
      is_used: false
      created_at: Date
      used_at: Date
      created_by_username: string
    }

export type RoleCodesUserRole = Extract<User['role'], 'admin' | 'jury' | 'organizer'>

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
