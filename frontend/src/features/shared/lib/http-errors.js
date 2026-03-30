export const parseApiError = async (response, fallbackMessage) => {
  try {
    const data = await response.json()
    if (typeof data === 'string') return data
    if (data.detail) return data.detail
    return JSON.stringify(data)
  } catch {
    return fallbackMessage
  }
}
