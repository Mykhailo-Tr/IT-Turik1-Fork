import { API_BASE } from '@/features/shared/config/api'
import axios from 'axios'

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export function isApiError(err: unknown) {
  return axios.isAxiosError(err)
}

export default apiClient
