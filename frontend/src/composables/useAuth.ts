import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

export function useAuth() {
  const store = useUserStore()
  const router = useRouter()
  const { user, isLoggedIn, isLoading } = storeToRefs(store)

  const logout = () => {
    store.logout()
    router.push('/')
  }

  return {
    user,
    isLoggedIn,
    isLoading,
    login: store.login,
    logout: logout,
    update: store.update,
    loadUser: store.loadUser,
    refresh: () => store.loadUser(true),
  }
}
