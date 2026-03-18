<template>
  <section class="page-shell">
    <article class="card profile-card">
      <div class="head">
        <div>
          <p class="section-eyebrow">User Center</p>
          <h1 class="section-title profile-title">My profile</h1>
        </div>
        <p class="meta">Joined: {{ formatDate(profile.created_at) || 'N/A' }}</p>
      </div>

      <div v-if="notification" :class="['notice', notification.type]">
        {{ notification.message }}
      </div>

      <div class="summary">
        <div class="item">
          <span>Username</span>
          <strong>{{ profile.username || '-' }}</strong>
        </div>
        <div class="item">
          <span>Email</span>
          <strong>{{ profile.email || '-' }}</strong>
        </div>
        <div class="item">
          <span>Role</span>
          <strong class="badge">{{ profile.role || '-' }}</strong>
        </div>
      </div>

      <form @submit.prevent="handleUpdate" class="form">
        <label class="form-label">
          Full name
          <input v-model="form.full_name" class="input-control" type="text" placeholder="John Doe" />
        </label>

        <label class="form-label">
          Phone
          <input v-model="form.phone" class="input-control" type="text" placeholder="+380..." />
          <small v-if="errors.phone" class="text-error">{{ errors.phone[0] }}</small>
        </label>

        <label class="form-label">
          City
          <input v-model="form.city" class="input-control" type="text" placeholder="Kyiv" />
        </label>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Saving...' : 'Save changes' }}
        </button>
      </form>

      <div class="danger-zone">
        <p class="danger-text">Danger zone: this action permanently deletes your account.</p>
        <button class="btn-danger" :disabled="loading || isDeleting" @click="openDeleteModal" type="button">
          Delete account
        </button>
      </div>
    </article>

    <div v-if="isDeleteModalOpen" class="modal-backdrop" @click.self="closeDeleteModal">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="delete-title">
        <h3 id="delete-title">Delete account</h3>
        <p class="modal-text">
          This action cannot be undone. Enter
          <code>{{ expectedDeleteText }}</code>
          to confirm.
        </p>

        <input
          v-model="deleteConfirmInput"
          class="input-control"
          type="text"
          :placeholder="expectedDeleteText"
          :disabled="isDeleting"
        />

        <p v-if="deleteError" class="text-error modal-error">{{ deleteError }}</p>

        <div class="modal-actions">
          <button class="btn-cancel" type="button" :disabled="isDeleting" @click="closeDeleteModal">
            Cancel
          </button>
          <button class="btn-danger" type="button" :disabled="!canConfirmDelete" @click="handleDeleteAccount">
            {{ isDeleting ? 'Deleting...' : 'Delete permanently' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE } from '@/config/api'

const profile = ref({})
const form = ref({ full_name: '', phone: '', city: '' })
const loading = ref(false)
const errors = ref({})
const notification = ref(null)
const router = useRouter()
const isDeleteModalOpen = ref(false)
const deleteConfirmInput = ref('')
const deleteError = ref('')
const isDeleting = ref(false)

const expectedDeleteText = computed(() => profile.value.username || '')
const canConfirmDelete = computed(
  () =>
    Boolean(expectedDeleteText.value) &&
    deleteConfirmInput.value === expectedDeleteText.value &&
    !isDeleting.value,
)

const logoutToLogin = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  localStorage.removeItem('needs_onboarding')
  router.push('/login')
}

const fetchProfile = async () => {
  const token = localStorage.getItem('access')
  const res = await fetch(`${API_BASE}/api/accounts/profile/`, {
    headers: { Authorization: `Bearer ${token}` },
  })

  if (res.status === 401) {
    logoutToLogin()
    return
  }

  if (res.ok) {
    const data = await res.json()
    if (data.needs_onboarding) {
      localStorage.setItem('needs_onboarding', '1')
      router.push('/complete-profile')
      return
    }

    profile.value = data
    form.value = {
      full_name: data.full_name || '',
      phone: data.phone || '',
      city: data.city || '',
    }
  }
}

const handleUpdate = async () => {
  loading.value = true
  errors.value = {}
  notification.value = null

  const token = localStorage.getItem('access')
  try {
    const res = await fetch(`${API_BASE}/api/accounts/profile/`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(form.value),
    })

    if (res.status === 401) {
      logoutToLogin()
      return
    }

    const data = await res.json()

    if (res.ok) {
      notification.value = { type: 'success', message: 'Profile updated successfully.' }
      profile.value = { ...profile.value, ...data }
      return
    }

    errors.value = data
    notification.value = { type: 'error', message: 'Validation error. Please check your data.' }
  } catch {
    notification.value = { type: 'error', message: 'Server connection error.' }
  } finally {
    loading.value = false
  }
}

const openDeleteModal = () => {
  deleteConfirmInput.value = ''
  deleteError.value = ''
  isDeleteModalOpen.value = true
}

const closeDeleteModal = () => {
  if (isDeleting.value) {
    return
  }
  isDeleteModalOpen.value = false
}

const handleDeleteAccount = async () => {
  if (deleteConfirmInput.value !== expectedDeleteText.value) {
    deleteError.value = `Please enter "${expectedDeleteText.value}" exactly.`
    return
  }

  isDeleting.value = true
  deleteError.value = ''
  notification.value = null
  errors.value = {}

  const token = localStorage.getItem('access')
  try {
    const res = await fetch(`${API_BASE}/api/accounts/profile/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (res.status === 204 || res.status === 200) {
      logoutToLogin()
      return
    }

    if (res.status === 401) {
      logoutToLogin()
      return
    }

    notification.value = { type: 'error', message: 'Unable to delete account.' }
  } catch {
    notification.value = { type: 'error', message: 'Server connection error.' }
  } finally {
    isDeleting.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('uk-UA')
}

onMounted(fetchProfile)
</script>

<style scoped>
.profile-card {
  max-width: 760px;
  margin: 0 auto;
  padding: 1.4rem;
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

.profile-title {
  margin-top: 0.2rem;
}

.meta {
  margin: 0;
  color: var(--ink-500);
  font-size: 0.86rem;
}

.summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.6rem;
  margin-top: 1rem;
}

.item {
  border: 1px solid var(--line-soft);
  border-radius: 14px;
  padding: 0.7rem;
  background: rgba(255, 255, 255, 0.85);
}

.item span {
  display: block;
  color: var(--ink-500);
  font-size: 0.8rem;
}

.item strong {
  color: var(--ink-900);
}

.badge {
  display: inline-block;
  border-radius: 999px;
  background: rgba(20, 184, 166, 0.2);
  color: var(--brand-700);
  padding: 0.15rem 0.5rem;
  text-transform: uppercase;
  font-size: 0.74rem;
}

.form {
  margin-top: 1rem;
  display: grid;
  gap: 0.8rem;
}

.danger-zone {
  margin-top: 1.4rem;
  border-top: 1px dashed var(--line-strong);
  padding-top: 1rem;
}

.danger-text {
  margin: 0 0 0.6rem;
  color: #991b1b;
  font-weight: 600;
}

.btn-danger {
  border: 1px solid #dc2626;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 12px;
  padding: 0.7rem 1rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.btn-danger:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: grid;
  place-items: center;
  z-index: 50;
  padding: 1rem;
}

.modal-card {
  width: min(100%, 520px);
  background: #fff;
  border-radius: 16px;
  border: 1px solid var(--line-soft);
  box-shadow: var(--shadow-lg);
  padding: 1.2rem;
}

.modal-card h3 {
  margin: 0;
  font-family: var(--font-display);
}

.modal-text {
  margin: 0.7rem 0;
  color: var(--ink-700);
}

.modal-text code {
  background: #f1f5f9;
  border: 1px solid var(--line-soft);
  border-radius: 6px;
  padding: 0.1rem 0.35rem;
}

.modal-error {
  margin: 0.5rem 0 0;
}

.modal-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
}

.btn-cancel {
  border: 1px solid var(--line-strong);
  border-radius: 12px;
  padding: 0.7rem 1rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
  background: #fff;
}

.btn-cancel:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@media (max-width: 760px) {
  .profile-card {
    padding: 1rem;
  }

  .head {
    flex-direction: column;
    align-items: flex-start;
  }

  .summary {
    grid-template-columns: 1fr;
  }
}
</style>
