import { API_BASE } from '@/features/shared/config/api'
import router from '@/router'
import { useUserStore } from '@/stores/user'
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

apiClient.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 401) {
      const store = useUserStore()

      store.removeTokens()
      router.push('/login')
    }
    return Promise.reject(err)
  },
)

export function isApiError(err: unknown) {
  return axios.isAxiosError(err)
}

export default apiClient
