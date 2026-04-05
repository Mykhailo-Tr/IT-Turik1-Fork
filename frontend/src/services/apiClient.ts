import { API_BASE } from '@/features/shared/config/api'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
import router from '@/router'

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

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const { logout } = useUserStore()

      logout()
      router.push('/login')
    }
    return Promise.reject(err)
  },
)

export function isApiError(err: unknown) {
  return axios.isAxiosError(err)
}

export default apiClient
