import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'

export function useAuth() {
  const store = useUserStore()
  const { user, isLoggedIn, isLoading } = storeToRefs(store)

  return {
    user,
    isLoggedIn,
    isLoading,
    login: store.login,
    logout: store.logout,
    update: store.update,
    loadUser: store.loadUser,
    refresh: () => store.loadUser(true),
  }
}
