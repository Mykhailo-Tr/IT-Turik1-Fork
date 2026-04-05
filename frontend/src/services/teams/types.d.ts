import type { Invatation, JoinRequest, Team, User, UserId } from '../dbTypes'

export type GetTeamInfoResponse = Team & {
  members: Pick<User, 'id' | 'username' | 'email' | 'full_name' | 'role'>[]
  invitations: Invatation[] // TODO: maybe use Pick?
  join_requests: JoinRequest[] // TODO: add types
  my_invitation_status: boolean
  my_join_request_status: boolean
  is_member: boolean
  is_captain: boolean
  can_request_to_join: boolean
}

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

export type ManageJoinRequestAction = 'accept' | 'decline'

export interface ResendInvatationBody {
  user_id: UserId
}

export interface ChangeTeamVisibilityBody {
  is_public: boolean
}

export interface UpdateTeamInfoBody {
  name: string
  email: string
  organization: string
  contact_telegram: string
  contact_discord: string
}

export interface AddMemberBody {
  user_id: UserId
}

type GetTeamsResponse = Team & {
  is_captain: boolean
  is_member: boolean
  my_invitation_status: boolean
  my_join_request_status: boolean
  can_request_to_join: boolean
}
