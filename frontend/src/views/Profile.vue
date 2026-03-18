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
    </article>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE } from '@/config/api'

const profile = ref({})
const form = ref({ full_name: '', phone: '', city: '' })
const loading = ref(false)
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
