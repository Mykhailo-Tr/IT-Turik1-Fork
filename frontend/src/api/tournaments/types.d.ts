import type { Round, Tournament, TournamentId } from '../dbTypes'

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

// Create Round
//  "tournament": 1,
//   "position": 2,
//   "name": "Final Stage",
//   "start_date": "2026-05-05T10:00:00Z",
//   "end_date": "2026-05-07T18:00:00Z",
//   "passing_count": 5

export type CreateRoundBody = Pick<
  Round,
  | 'name'
  | 'passing_count'
  | 'description'
  | 'tech_requirements'
  | 'must_have_requirements'
  | 'start_date'
  | 'end_date'
> & {
  tournament: TournamentId
}

export interface CreateRoundArgs {
  body: CreateRoundBody
}
