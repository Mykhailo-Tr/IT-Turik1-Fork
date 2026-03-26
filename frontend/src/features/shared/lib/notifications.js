import { computed, reactive, readonly } from 'vue'

const DEFAULT_DURATION_MS = 4200
const MIN_DURATION_MS = 3000
const MAX_DURATION_MS = 5000

const state = reactive({
  current: null,
  queue: [],
})

let notificationId = 0
let notificationTimerId = null

const normalizeDuration = (duration) => {
  if (!Number.isFinite(duration)) return DEFAULT_DURATION_MS
  return Math.min(MAX_DURATION_MS, Math.max(MIN_DURATION_MS, Math.round(duration)))
}

const clearNotificationTimer = () => {
  if (notificationTimerId) {
    clearTimeout(notificationTimerId)
    notificationTimerId = null
  }
}

const sameNotification = (first, second) =>
  Boolean(first) &&
  Boolean(second) &&
  first.message === second.message &&
  first.type === second.type

const scheduleDismiss = (duration) => {
  clearNotificationTimer()
  notificationTimerId = setTimeout(() => {
    notificationTimerId = null
    if (state.queue.length > 0) {
      const next = state.queue.shift()
      showNow(next)
      return
    }
    state.current = null
  }, duration)
}

const showNow = (payload) => {
  state.current = { ...payload, id: ++notificationId }
  scheduleDismiss(payload.duration)
}

const clearNotification = (clearQueue = false) => {
  clearNotificationTimer()
  if (clearQueue) {
    state.queue.length = 0
    state.current = null
    return
  }
  if (state.queue.length > 0) {
    const next = state.queue.shift()
    showNow(next)
    return
  }
  state.current = null
}

const showNotification = (message, type = 'info', options = {}) => {
  const text = String(message || '').trim()
  if (!text) return

  const payload = {
    message: text,
    type: String(type || 'info'),
    duration: normalizeDuration(options.duration),
  }

  if (options.mode === 'queue' && state.current) {
    const lastQueued = state.queue[state.queue.length - 1]
    if (sameNotification(state.current, payload) || sameNotification(lastQueued, payload)) return
    state.queue.push(payload)
    return
  }

  if (sameNotification(state.current, payload)) {
    // Same notice fired again: refresh lifetime without creating a duplicate.
    scheduleDismiss(payload.duration)
    return
  }

  showNow(payload)
}

const notification = computed(() => state.current)

export const useGlobalNotification = () => ({
  notification: readonly(notification),
  showNotification,
  hideNotification: clearNotification,
  clearNotificationQueue: () => {
    state.queue.length = 0
  },
})
