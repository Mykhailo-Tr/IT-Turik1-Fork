import { isAxiosError, type AxiosError } from 'axios'
import { accountsService } from './accounts'
import { teamsService } from './teams'
import { notificationsService } from './notifications'

const $api = {
  accounts: accountsService,
  teams: teamsService,
  notifications: notificationsService,
}

export default $api

export interface ApiError<DetailsFields extends string = string> {
  code: string
  message: string
  details: Partial<Record<DetailsFields, string[]>>
}

export function parseError<DetailsFields extends string = string>(
  error?: AxiosError<ApiError<DetailsFields>> | null,
): ApiError<DetailsFields> | undefined {
  if (isAxiosError(error)) {
    if (error.response?.data) {
      const data = error.response.data

      return data
    }

    if (error.request) {
      return {
        message: 'Network error. Try again',
        code: 'unexpected_error',
        details: {},
      }
    }
  }
}
