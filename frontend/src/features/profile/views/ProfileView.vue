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

      <div v-if="loadingProfile" class="state-box">Loading profile...</div>
      <div v-else-if="profileError" class="state-box error">{{ profileError }}</div>
      <div v-else class="details">
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
        <div class="item">
          <span>Full name</span>
          <strong>{{ profile.full_name || '-' }}</strong>
        </div>
        <div class="item">
          <span>Phone</span>
          <strong>{{ profile.phone || '-' }}</strong>
        </div>
        <div class="item">
          <span>City</span>
          <strong>{{ profile.city || '-' }}</strong>
        </div>
        <div class="item item-wide">
          <span>Teams</span>
          <div class="team-list">
            <router-link
              v-for="team in profile.teams || []"
              :key="team.id"
              :to="`/teams/${team.id}`"
              class="team-link"
            >
              {{ team.name }}
            </router-link>
            <p v-if="!(profile.teams || []).length" class="text-muted">No teams yet.</p>
          </div>
        </div>
      </div>

      <div class="actions">
        <button class="btn-primary" type="button" :disabled="loadingProfile" @click="goToEditProfile">
          Edit Profile
        </button>
        <button class="btn-secondary" type="button" :disabled="loadingProfile || isDeleting" @click="logoutToLogin">
          Log Out
        </button>
      </div>

      <div class="danger-zone">
        <p class="danger-text">Danger zone: this action permanently deletes your account.</p>
        <button class="btn-danger" :disabled="loadingProfile || isDeleting" @click="openDeleteModal" type="button">
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
import { API_BASE } from '@/features/shared/config/api'
import { useGlobalNotification } from '@/features/shared/lib/notifications'

const profile = ref({})
const profileError = ref('')
const loadingProfile = ref(true)

const router = useRouter()
const { showNotification, hideNotification } = useGlobalNotification()
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

const goToEditProfile = () => {
  router.push('/profile/edit')
}

const fetchProfile = async () => {
  loadingProfile.value = true
  profileError.value = ''

  const token = localStorage.getItem('access')
  try {
    const res = await fetch(`${API_BASE}/api/accounts/profile/`, {
      headers: { Authorization: `Bearer ${token}` },
    })

    if (res.status === 401) {
      logoutToLogin()
      return
    }

    if (!res.ok) {
      profileError.value = 'Could not load profile information.'
      return
    }

    const data = await res.json()
    if (data.needs_onboarding) {
      localStorage.setItem('needs_onboarding', '1')
      router.push('/complete-profile')
      return
    }

    profile.value = data
  } catch {
    profileError.value = 'Server connection error.'
  } finally {
    loadingProfile.value = false
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
  hideNotification()

  const token = localStorage.getItem('access')
  try {
    const res = await fetch(`${API_BASE}/api/accounts/profile/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (res.status === 204 || res.status === 200 || res.status === 401) {
      logoutToLogin()
      return
    }

    showNotification('Unable to delete account.', 'error')
  } catch {
    showNotification('Server connection error.', 'error')
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

.state-box {
  margin-top: 1rem;
  border-radius: 14px;
  border: 1px solid var(--line-soft);
  padding: 0.9rem 1rem;
  background: rgba(255, 255, 255, 0.85);
}

.state-box.error {
  color: #991b1b;
  border-color: rgba(220, 38, 38, 0.25);
  background: rgba(254, 242, 242, 0.9);
}

.details {
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

.item-wide {
  grid-column: 1 / -1;
}

.team-list {
  margin-top: 0.4rem;
  display: grid;
  gap: 0.35rem;
}

.team-list p {
  margin: 0;
}

.team-link {
  color: var(--brand-700);
  text-decoration: none;
  font-weight: 700;
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

.actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.btn-secondary {
  border: 1px solid var(--line-strong);
  border-radius: 12px;
  padding: 0.8rem 1rem;
  font: inherit;
  font-weight: 700;
  background: #fff;
  color: var(--ink-800);
  cursor: pointer;
}

.btn-secondary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
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

  .details {
    grid-template-columns: 1fr;
  }

  .actions {
    flex-direction: column;
  }
}
</style>
<style scoped src="../../teams/styles/status-tags.css"></style>
