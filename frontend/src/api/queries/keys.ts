import type { GetRoleCodesFilter } from '@/api/services/accounts/types'
import type { TeamId, TournamentId } from '@/api/dbTypes'
import type { GetTournamentsArgs } from '@/api/services/tournaments/types'

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

export const touranmentsKeys = {
  allTouranments: () => ['tournaments'],
  'tournaments-list': (args: GetTournamentsArgs) => [
    'tournaments',
    args.page,
    args.searchQuery,
    args.status,
    args.pageSize,
  ],
  touranment: (id: TournamentId) => ['tournaments', id],
  'eligible-teams': () => ['eligible-teams'],
  'registered-teams': (id: TournamentId) => ['registered-teams', id],
  rounds: (id: TournamentId) => ['rounds', id],
  'current-round': (id: TournamentId) => ['current-round', id],
}
