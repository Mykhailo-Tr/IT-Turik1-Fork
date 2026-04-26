import type { Round, Team, TeamId, Tournament, TournamentId } from '@/api/dbTypes'

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
