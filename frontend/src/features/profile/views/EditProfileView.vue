<template>
  <section class="page-shell">
    <article class="card profile-card">
      <div class="head">
        <div>
          <p class="section-eyebrow">User Center</p>
          <h1 class="section-title profile-title">Edit Profile</h1>
        </div>
      </div>

      <p class="section-subtitle">
        Update your account details below and save your changes.
      </p>

      <div v-if="notification" :class="['notice', notification.type]">
        {{ notification.message }}
      </div>

      <div v-if="loadingProfile" class="state-box">Loading profile...</div>
      <div v-else-if="profileError" class="state-box error">{{ profileError }}</div>

      <form v-else @submit.prevent="handleUpdate" class="form-grid">
        <label class="form-label">
          Username
          <input v-model="form.username" class="input-control" type="text" placeholder="johndoe" />
          <small v-if="errors.username" class="text-error">{{ errors.username[0] }}</small>
        </label>

        <label class="form-label">
          Phone
          <PhoneField v-model="form.phone" :error="errors.phone?.[0]" />
        </label>

        <label class="form-label">
          Full name
          <input v-model="form.full_name" class="input-control" type="text" placeholder="John Doe" />
        </label>

        <label class="form-label full-width">
          City
          <input v-model="form.city" class="input-control" type="text" placeholder="Kyiv" />
        </label>

        <div class="actions full-width">
          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Save changes' }}
          </button>
          <button class="btn-secondary" type="button" :disabled="loading" @click="goBackToProfile">
            Cancel
          </button>
        </div>
      </form>
    </article>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PhoneField from '@/features/shared/components/forms/PhoneField.vue'
import { API_BASE } from '@/features/shared/config/api'

const form = ref({ username: '', full_name: '', phone: '', city: '' })
const loading = ref(false)
const loadingProfile = ref(true)
const profileError = ref('')
const errors = ref({})
const notification = ref(null)
const router = useRouter()

const logoutToLogin = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  localStorage.removeItem('needs_onboarding')
  router.push('/login')
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

    form.value = {
      username: data.username || '',
      full_name: data.full_name || '',
      phone: data.phone || '',
      city: data.city || '',
    }
  } catch {
    profileError.value = 'Server connection error.'
  } finally {
    loadingProfile.value = false
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
      setTimeout(() => {
        router.push('/profile')
      }, 550)
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

const goBackToProfile = () => {
  router.push('/profile')
}

onMounted(fetchProfile)
</script>

<style scoped>
.profile-card {
  max-width: 760px;
  margin: 0 auto;
  padding: 1.5rem;
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

.section-subtitle {
  margin-bottom: 0;
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

.form-grid {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.full-width {
  grid-column: 1 / -1;
}

.actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-top: 0.35rem;
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

@media (max-width: 760px) {
  .profile-card {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .full-width {
    grid-column: auto;
  }

  .actions {
    flex-direction: column;
  }
}
</style>

