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
  users: () => ['users'],
  roleCodes: (filter?: GetRoleCodesFilter) => ['role-codes', filter?.role ?? 'all'],
}

export const notificationKeys = {
  all: ['notifications'] as const,
  lists: () => [...notificationKeys.all, 'list'] as const,
  list: (page: number, pageSize: number) => [...notificationKeys.lists(), { page, pageSize }] as const,
  unreadCount: () => [...notificationKeys.all, 'unread-count'] as const,
  settings: () => [...notificationKeys.all, 'settings'] as const,
}
