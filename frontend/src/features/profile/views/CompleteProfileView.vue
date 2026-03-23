<template>
  <section class="page-shell centered">
    <article class="card complete-card">
      <p class="section-eyebrow">Final Step</p>
      <h1 class="section-title">Complete your profile</h1>
      <p class="section-subtitle">
        Choose your role and review your account details before continuing.
      </p>

      <p v-if="message" :class="['notice', messageType]">{{ message }}</p>

      <form class="form-grid" @submit.prevent="handleSubmit">
        <label class="form-label">
          Username
          <input v-model="form.username" class="input-control" type="text" required />
          <small v-if="errors.username" class="text-error">{{ errors.username[0] }}</small>
        </label>

        <label class="form-label">
          Role
          <select v-model="form.role" class="select-control" required>
            <option value="" disabled>Select role</option>
            <option value="team">Team Member</option>
            <option value="organizer">Organizer</option>
            <option value="jury">Jury</option>
            <option value="admin">Admin</option>
          </select>
          <small v-if="errors.role" class="text-error">{{ errors.role[0] }}</small>
        </label>

        <label class="form-label full-width">
          Full name
          <input v-model="form.full_name" class="input-control" type="text" />
        </label>

        <label class="form-label">
          Phone
          <PhoneField v-model="form.phone" :error="errors.phone?.[0]" placeholder="Enter phone number" />
        </label>

        <label class="form-label">
          City
          <input v-model="form.city" class="input-control" type="text" />
        </label>

        <button class="btn-primary submit-btn" :disabled="loading || bootLoading" type="submit">
          {{ loading ? 'Saving...' : 'Complete registration' }}
        </button>
      </form>
    </article>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import PhoneField from '@/features/shared/components/forms/PhoneField.vue'
import { API_BASE } from '@/features/shared/config/api'

const router = useRouter()
const loading = ref(false)
const bootLoading = ref(true)
const message = ref('')
const messageType = ref('success')
const errors = ref({})

const form = ref({
  username: '',
  role: '',
  full_name: '',
  phone: '',
  city: '',
})

const logoutToLogin = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  localStorage.removeItem('needs_onboarding')
  router.push('/login')
}

const handleSubmit = async () => {
  loading.value = true
  errors.value = {}
  message.value = ''

  const token = localStorage.getItem('access')
  try {
    const response = await fetch(`${API_BASE}/api/accounts/profile/`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(form.value),
    })

    if (response.status === 401) {
      logoutToLogin()
      return
    }

    const data = await response.json()
    if (!response.ok) {
      errors.value = data
      messageType.value = 'error'
      message.value = 'Please fix form errors and try again.'
      return
    }

    localStorage.removeItem('needs_onboarding')
    messageType.value = 'success'
    message.value = 'Profile completed successfully.'
    router.push('/')
  } catch {
    messageType.value = 'error'
    message.value = 'Server connection error.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const token = localStorage.getItem('access')
  if (!token) {
    logoutToLogin()
    return
  }

  try {
    const response = await fetch(`${API_BASE}/api/accounts/profile/`, {
      headers: { Authorization: `Bearer ${token}` },
    })

    if (response.status === 401) {
      logoutToLogin()
      return
    }

    if (!response.ok) {
      messageType.value = 'error'
      message.value = 'Could not load your profile.'
      return
    }

    const data = await response.json()
    if (!data.needs_onboarding) {
      localStorage.removeItem('needs_onboarding')
      router.push('/')
      return
    }

    form.value = {
      username: data.username || '',
      role: '',
      full_name: data.full_name || '',
      phone: data.phone || '',
      city: data.city || '',
    }
  } catch {
    messageType.value = 'error'
    message.value = 'Server connection error.'
  } finally {
    bootLoading.value = false
  }
})
</script>

<style scoped>
.complete-card {
  width: min(100%, 720px);
  padding: 2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.full-width {
  grid-column: 1 / -1;
}

.submit-btn {
  margin-top: 0.5rem;
  grid-column: 1 / -1;
}

@media (max-width: 760px) {
  .complete-card {
    padding: 1.3rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .submit-btn {
    grid-column: auto;
  }
}
</style>

