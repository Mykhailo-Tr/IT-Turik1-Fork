const AUTH_STORAGE_KEYS = ['access', 'refresh', 'needs_onboarding']

export const clearAuthSession = () => {
  for (const key of AUTH_STORAGE_KEYS) {
    localStorage.removeItem(key)
  }
}

// TODO: remove this bullshit???

export const createAuthHeaders = (json = false) => {
  const token = localStorage.getItem('access')
  const headers = { Authorization: `Bearer ${token}` }
  if (json) headers['Content-Type'] = 'application/json'
  return headers
}

// TODO: remove this bullshit???

export const logoutToLogin = (router) => {
  clearAuthSession()
  router.push('/login')
}
