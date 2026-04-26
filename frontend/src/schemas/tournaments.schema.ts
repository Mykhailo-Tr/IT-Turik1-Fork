import { combineDateAndTime } from '@/lib/date'
import { tiptapJsonToText } from '@/lib/utils'
import * as v from 'valibot'

export const TimeSchema = v.pipe(
  v.string(),
  v.regex(/^([01]\d|2[0-3]):[0-5]\d$/, 'Time must be in HH:MM format (00:00–23:59)'),
)

export const CreateTournamentSchema = v.pipe(
  v.object({
    name: v.pipe(v.string(), v.minLength(1, 'Tournament name is required')),
    description: v.pipe(
      v.string(),
      v.minLength(20, 'Description must be at least 20 characters long'),
    ),
    startDate: v.date(),
    startTime: TimeSchema,
    endDate: v.date(),
    endTime: TimeSchema,
    rounds_count: v.pipe(v.number('must be a number'), v.minValue(1, 'Rounds must be at least 1')),
    max_teams: v.pipe(
      v.number('must be a number'),
      v.minValue(2, 'Maximum teams must be at least 2'),
    ),
    min_team_members: v.pipe(
      v.number('must be a number'),
      v.minValue(2, 'Minimum team members must be at least 2'),
    ),
  }),

  v.forward(
    v.partialCheck(
      [['startDate'], ['endDate'], ['startTime'], ['endTime']],
      (input) => {
        const combinedStartDate = combineDateAndTime(input.startDate, input.startTime)
        const combinedEndDate = combineDateAndTime(input.endDate, input.endTime)
        return combinedEndDate > combinedStartDate
      },
      'End date/time must be after start date/time',
    ),
    ['endDate'],
  ),
)

function tiptapJsonMinLength(min: number, message: string) {
  return v.pipe(
    v.unknown(),
    v.check((value) => tiptapJsonToText(value).length >= min, message),
  )
}

export const CreateRoundSchema = v.pipe(
  v.object({
    name: v.pipe(v.string(), v.minLength(1, 'Name is required')),
    description: tiptapJsonMinLength(10, 'Description must be at least 10 characters long'),
    passing_count: v.pipe(v.number(), v.minValue(1, 'Minimum 1 team shoud pass')),
    tech_requirements: tiptapJsonMinLength(
      10,
      'Technical requirements must be at least 10 characters long',
    ),
    must_have_requirements: tiptapJsonMinLength(
      10,
      'Must have must be at least 10 characters long',
    ),
    start_date: v.date(),
    end_date: v.date(),
  }),

  v.forward(
    v.partialCheck(
      [['start_date'], ['end_date']],
      (input) => input.end_date > input.start_date,
      'End date must be after start date',
    ),
    ['end_date'],
  ),
)
