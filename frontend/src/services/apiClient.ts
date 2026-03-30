import { API_BASE } from '@/features/shared/config/api'
import axios from 'axios'

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

// TODO: catch 401 responses?
apiClient.interceptors.response.use(
  function (response) {
    return response
  },
  function (error) {
    console.error('Looks like there was a problem')
    return Promise.reject(error)
  },
)

export function isApiError(err: unknown) {
  return axios.isAxiosError(err)
}

export default apiClient
