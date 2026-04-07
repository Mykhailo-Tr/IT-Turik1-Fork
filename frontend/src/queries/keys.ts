import type { GetRoleCodesFilter } from '@/api/accounts/types'
import type { TeamId, UserRole } from '@/api/dbTypes'

export const teamKeys = {
  allTeams: () => ['teams'],
  team: (id: TeamId) => ['teams', id],
}

export const accountKeys = {
  profile: () => ['profile'],
  users: () => ['users'],
  roleCodes: (filter?: GetRoleCodesFilter) => ['role-codes', filter?.role ?? 'all'],
}
