<template>
  <section class="page-shell centered">
    <article class="card activate-card">
      <p class="section-eyebrow">Email Verification</p>
      <h1 class="section-title activate-title">Account activation</h1>

      <p v-if="status === 'loading'" class="text-muted status">Checking your activation token...</p>

      <div v-if="status === 'success'" class="notice success">
        {{ message }}
        <router-link to="/login">Go to sign in</router-link>
      </div>

      <div v-if="status === 'error'" class="notice error">
        {{ message }}
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { API_BASE } from '@/features/shared/config/api'

const route = useRoute()
const status = ref('loading')
const message = ref('')

onMounted(async () => {
  const { uid, token } = route.params

  try {
    const res = await fetch(`${API_BASE}/api/accounts/activate/${uid}/${token}/`)
    const data = await res.json()

    if (res.ok) {
      status.value = 'success'
      message.value = data.message
      return
    }

    status.value = 'error'
    message.value = data.message || 'Activation failed.'
  } catch {
    status.value = 'error'
    message.value = 'Server is unavailable.'
  }
})
</script>

<style scoped>
.activate-card {
  width: min(100%, 520px);
  padding: 2rem;
  text-align: center;
}

.activate-title {
  margin-top: 0.2rem;
}

.status {
  margin-top: 1rem;
}

.notice {
  display: grid;
  gap: 0.45rem;
}

.notice a {
  color: var(--brand-700);
  text-decoration: none;
  font-weight: 700;
}
</style>
