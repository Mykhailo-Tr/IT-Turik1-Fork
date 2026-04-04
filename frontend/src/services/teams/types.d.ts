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

export type ManageJoinRequestAction = 'accept' | 'decline'

export interface ResendInvatationBody {
  user_id: UserId
}

export interface ChangeTeamVisibilityBody {
  is_public: boolean
}
