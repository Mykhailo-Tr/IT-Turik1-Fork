import type { Round, Tournament, TournamentId } from '@/api/dbTypes'

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

// TODO

export type GetTournamentInfoResponse = Tournament & {
  rounds: [] // TODO
}

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
