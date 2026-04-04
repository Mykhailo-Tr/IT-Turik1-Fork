<template>
  <section class="page-shell">
    <ui-card class="admin-card">
      <p class="section-eyebrow">Admin</p>
      <h1 class="section-title">Activation Codes</h1>
      <p class="section-subtitle">
        Generate and monitor one-time registration codes for restricted roles.
      </p>

      <p v-if="statusMessage" :class="['notice', statusType]">{{ statusMessage }}</p>

      <div v-if="loading" class="state-box">Loading...</div>

      <div v-else-if="forbidden" class="state-box error">You do not have access to this page.</div>

      <template v-else>
        <div class="counts">
          <div class="count-item" v-for="role in restrictedRoles" :key="role">
            <span>{{ role }}</span>
            <strong>{{ activeCounts[role] || 0 }}/10 active</strong>
          </div>
        </div>

        <form class="generator" @submit.prevent="handleGenerate">
          <label class="form-label">
            Role
            <ui-select
              v-model="generateForm.role"
              :options="[
                { value: 'jury', label: 'Jury' },
                { value: 'organizer', label: 'Organizer' },
                { value: 'admin', label: 'Admin' },
              ]"
              required
            >
              <option value="jury">Jury</option>
              <option value="organizer">Organizer</option>
              <option value="admin">Admin</option>
            </ui-select>
            <small v-if="errors?.role" class="text-error">{{ errors.role[0] }}</small>
          </label>

          <label class="form-label">
            Quantity
            <ui-input
              v-model.number="generateForm.quantity"
              type="number"
              min="1"
              max="10"
              required
            />
            <small v-if="errors?.quantity" class="text-error">{{ errors.quantity[0] }}</small>
          </label>

          <ui-button type="submit" class="generate-btn" :disabled="submitting">
            {{ submitting ? 'Generating...' : 'Generate Codes' }}
          </ui-button>
        </form>

        <div class="filters">
          <!-- TODO: select component wrapped around label??????? -->
          <!-- Fix later cuz it depends on some class styles -->
          <label class="form-label">
            Filter by role

            <ui-select
              v-model="selectedRoleFilter"
              :options="[
                { value: 'all', label: 'All restricted roles' },
                { value: 'jury', label: 'Jury' },
                { value: 'organizer', label: 'Organizer' },
                { value: 'admin', label: 'Admin' },
              ]"
            >
            </ui-select>
          </label>
        </div>

        <div class="codes-list">
          <article class="code-item" v-for="code in codes" :key="code.id">
            <div class="code-head">
              <strong class="mono">{{ code.code }}</strong>
              <span :class="['status-pill', code.is_used ? 'used' : 'active']">
                {{ code.is_used ? 'Used' : 'Active' }}
              </span>
            </div>
            <p><strong>Role:</strong> {{ code.role }}</p>
            <p><strong>Created:</strong> {{ formatDateTime(code.created_at) }}</p>
            <p><strong>Created by:</strong> {{ code.created_by_username || '-' }}</p>
            <p><strong>Used by:</strong> {{ code.is_used ? code.used_by : '-' }}</p>
            <p><strong>Used at:</strong> {{ code.used_at ? formatDateTime(code.used_at) : '-' }}</p>
          </article>
          <p v-if="!codes.length" class="text-muted">No codes found for current filter.</p>
        </div>
      </template>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import $api from '@/services'
import { isApiError } from '@/services/apiClient'
import type { RoleCode, RoleCodesUserRole } from '@/services/accounts'
import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiSelect from '@/components/UiSelect.vue'
import UiCard from '@/components/UiCard.vue'

const router = useRouter()
const loading = ref(true)
const submitting = ref(false)
const forbidden = ref(false)
const statusMessage = ref('')
const statusType = ref('success')
const errors = ref<{
  role: string[]
  quantity: string[]
} | null>(null)
const codes = ref<RoleCode[]>([])
const activeCounts = ref({ jury: 0, organizer: 0, admin: 0 })
const restrictedRoles = ['jury', 'organizer', 'admin'] as const
const selectedRoleFilter = ref<RoleCodesUserRole | 'all'>('all')
const generateForm = ref({
  role: 'jury',
  quantity: 1,
})

watch(selectedRoleFilter, async () => {
  await fetchCodes()
})

const fetchCodes = async () => {
  loading.value = true
  statusMessage.value = ''
  errors.value = null

  try {
    const response = await $api.accounts.getRoleCodes({
      role: selectedRoleFilter.value,
    })

    forbidden.value = false
    codes.value = response.data.codes || []
    activeCounts.value = response.data.active_counts || activeCounts.value
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        if (err.response.status === 401) return router.push('/login')
        if (err.response.status === 403) {
          forbidden.value = true
          return
        }

        statusType.value = 'error'
        statusMessage.value = err.response.data.detail || 'Unable to load activation codes.'
      } else {
        statusType.value = 'error'
        statusMessage.value = 'Server connection error.'
      }
    }
  } finally {
    loading.value = false
  }
}

const handleGenerate = async () => {
  submitting.value = true
  errors.value = null
  statusMessage.value = ''

  try {
    const response = await $api.accounts.generateCodes(generateForm.value)

    statusType.value = 'success'
    statusMessage.value = `Generated ${response.data.created?.length || 0} code(s) successfully.`
    activeCounts.value = response.data.active_counts || activeCounts.value
    await fetchCodes()
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        if (err.response.status === 401) return router.push('/login')
        if (err.response.status === 403) {
          forbidden.value = true
          return
        }

        errors.value = err.response.data
        statusType.value = 'error'
        statusMessage.value = err.response.data.detail || 'Unable to generate codes.'
      } else {
        statusType.value = 'error'
        statusMessage.value = 'Server connection error.'
      }
    }
  } finally {
    submitting.value = false
  }
}

const formatDateTime = (value: string | number | Date) => {
  if (!value) return '-'
  return new Date(value).toLocaleString()
}

onMounted(fetchCodes)
</script>

<style scoped>
.admin-card {
  width: min(100%, 980px);
  margin: 0 auto;
  padding: 1.6rem;
}

.counts {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
  margin: 0.8rem 0 1rem;
}

.count-item {
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  padding: 0.8rem;
  background: rgba(255, 255, 255, 0.86);
  display: grid;
  gap: 0.3rem;
}

.generator {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
  align-items: end;
  margin-bottom: 1rem;
}

.generate-btn {
  height: fit-content;
}

.filters {
  width: min(320px, 100%);
  margin-bottom: 1rem;
}

.codes-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 0.75rem;
}

.code-item {
  border: 1px solid var(--line-soft);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.86);
  padding: 0.9rem;
  display: grid;
  gap: 0.35rem;
}

.code-item p {
  margin: 0;
  color: var(--ink-700);
}

.code-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
  overflow-wrap: anywhere;
}

.status-pill {
  border-radius: 999px;
  padding: 0.18rem 0.55rem;
  font-size: 0.75rem;
  font-weight: 700;
}

.status-pill.active {
  background: rgba(22, 163, 74, 0.18);
  color: #166534;
}

.status-pill.used {
  background: rgba(148, 163, 184, 0.25);
  color: #334155;
}

@media (max-width: 900px) {
  .counts {
    grid-template-columns: 1fr;
  }

  .generator {
    grid-template-columns: 1fr;
  }
}
</style>
