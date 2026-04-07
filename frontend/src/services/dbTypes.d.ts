// ── User ────────────────────────────────────────────────────
export type UserId = number
export type UserRole = 'admin' | 'team' | 'jury' | 'organizer'

export interface User {
  id: UserId
  username: string
  email: string
  role: 'admin' | 'team' | 'jury' | 'organizer'
  full_name: string
  phone: string
  city: string
  created_at: Date
}

// ── Team ────────────────────────────────────────────────────
export type TeamId = number

export interface Team {
  id: TeamId
  name: string
  email: string
  members: Pick<User, 'id' | 'email' | 'username' | 'full_name' | 'role'>[]
  is_public: boolean
  captain_id: UserId
  organization: string
  contact_telegram: string
  contact_discord: string
}

// ── Invatation ────────────────────────────────────────────────────
type InvitationId = number
type InvatitionStatus = 'invited' | 'accepted' | 'declined'

interface Invitation {
  id: InvatationId
  team: Team
  user: Pick<User, 'id' | 'username' | 'email' | 'full_name' | 'role'>
  status: InvatationStatus
  created_at: Date
  responded_at: Date | null
  invited_by: User
}

// ── Join Request ────────────────────────────────────────────────────
type JoinRequestId = number
type JoinRequestStatus = 'pending' | 'accepted' | 'declined'

interface JoinRequest {
  id: JoinRequestId
  status: JoinRequestStatus
  user: Pick<User, 'id' | 'username' | 'email' | 'full_name' | 'role'>
  reviewed_by_id: UserId | null
  reviewed_at: Date | null
}
