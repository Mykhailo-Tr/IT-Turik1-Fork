import type { Round, Team, TeamId, Tournament, TournamentId, TournamentStatus } from '@/api/dbTypes'

// Get tournaments
export interface GetTournamentsArgs {
  page: number
  pageSize?: number
  searchQuery?: string
  status?: Exclude<TournamentStatus, 'draft'>[]
}

export interface GetTournamentsResponse {
  // TODO: add rounds type annotation
  data: (Pick<
    Tournament,
    | 'id'
    | 'name'
    | 'description'
    | 'start_date'
    | 'end_date'
    | 'max_teams'
    | 'min_team_members'
    | 'status'
  > & { rounds: [] })[]
  total: number
}

// Get tournaments
export interface GetTournamentsArgs {
  page: number
  pageSize?: number
  searchQuery?: string
}

// Create tournament
export type CreateTournamentBody = Pick<
  Tournament,
  | 'name'
  | 'description'
  | 'start_date'
  | 'end_date'
  | 'rounds_count'
  | 'max_teams'
  | 'min_team_members'
>

export interface CreateTournamentArgs {
  body: CreateTournamentBody
}

// Tournament info
export interface GetTournamentInfoArgs {
  id: TournamentId
}

export type GetTournamentInfoResponse = Tournament & {
  rounds: [] // TODO
}

// Get registered teams
export interface GetRegisteredTeamsArgs {
  id: TournamentId
}

export type GetRegisteredTeamsResponse = (Pick<Team, 'id' | 'name' | 'is_public'> & {
  members_count: number
  is_active: boolean
})[]

// Tournament rounds
export interface GetRoundsArgs {
  id: TournamentId
}

export type GetRoundsResponse = Round[]

// Get eligible teams
export interface GetEligibleTeamsArgs {
  id: TournamentId
}

export type GetEligibleTeamsResponse = (Pick<Team, 'id' | 'name'> & {
  members_count: number
})[]

// Create round
export type CreateRoundBody = Pick<
  Round,
  | 'name'
  | 'passing_count'
  | 'description'
  | 'tech_requirements'
  | 'must_have_requirements'
  | 'criteria'
  | 'start_date'
  | 'end_date'
> & {
  tournament: TournamentId
}

export interface CreateRoundArgs {
  id: TournamentId
  body: CreateRoundBody
}

// Get current round

export interface GetCurrentRoundArgs {
  id: TournamentId
}

export type GetCurrentRoundResponse = Pick<
  Round,
  'id' | 'name' | 'must_have_requirements' | 'tech_requirements'
> & {
  tournament_id: TournamentId
  tournamnet_name: Pick<Tournament, 'name'>
  task: Pick<Round, 'description'>
  deadline: string
}

// Register team

export interface RegisterTeamBody {
  team_id: TeamId
}

export interface RegisterTeamArgs {
  id: TournamentId
  body: RegisterTeamBody
}
