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

export interface GoogleLoginBody {
  credential: string
}

export interface RegisterBody {
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

interface ForgotPasswordBody {
  email: string
}

interface ResetPasswordBody {
  info: { uid: string; token: string }
  body: { new_password: string; confirm_password: string }
}

interface ValidatePasswordBody {
  info: { uid: string; token: string }
}

export type GetUsersResponse = Pick<User, 'id' | 'username' | 'email' | 'full_name' | 'role'>[]

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
