import type { GetRoleCodesFilter } from '@/api/accounts/types'
import type { TeamId, UserRole } from '@/api/dbTypes'

export const teamKeys = {
  allTeams: () => ['teams'],
  team: (id: TeamId) => ['teams', id],
  'join-requests': (id: TeamId) => ['team-join-requests', id],
  'team-invitations': (id: TeamId) => ['team-invitations', id],
}

export const accountKeys = {
  profile: () => ['profile'],
  user: (id: number) => ['user', id],
  users: () => ['users'],
  roleCodes: (filter?: GetRoleCodesFilter) => ['role-codes', filter?.role ?? 'all'],
}
