<template>
  <section class="page-shell teams-page">
    <ui-card>
      <p class="section-eyebrow">Teams</p>
      <h1 class="section-title">Create new team</h1>
      <p class="section-subtitle">Create a team and optionally add initial members.</p>
      <ui-button asLink class="back-link" variant="outline" size="sm" to="/teams"
        >Back to teams list</ui-button
      >

      <form class="form-grid" @submit.prevent="createTeam">
        <label class="form-label">
          Team name
          <ui-input v-model="form.name" required />
        </label>

        <label class="form-label">
          Team email
          <ui-input v-model="form.email" type="email" required />
        </label>

        <label class="form-label">
          Organization
          <ui-input v-model="form.organization" />
        </label>

        <label class="form-label toggle-field">
          <span>Team visibility</span>
          <div class="visibility-control">
            <span class="visibility-label">Private</span>
            <button
              type="button"
              class="visibility-switch"
              role="switch"
              :aria-checked="form.is_public ? 'true' : 'false'"
              :aria-label="`Team visibility: ${form.is_public ? 'Public' : 'Private'}`"
              @click="toggleVisibility"
              @keydown="onVisibilityKeydown"
            >
              <span class="switch-knob" :class="{ 'is-public': form.is_public }"></span>
            </button>
            <span class="visibility-label">Public</span>
          </div>
        </label>

        <label class="form-label">
          Telegram
          <ui-input
            v-model="form.contact_telegram"
            placeholder="@team_username"
            pattern="^@?[A-Za-z][A-Za-z0-9_]{4,31}$"
            title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
          />
        </label>

        <label class="form-label">
          Discord
          <ui-input
            v-model="form.contact_discord"
            placeholder="team.username"
            pattern="^@?(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?$"
            title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
          />
        </label>

        <div class="full-width">
          <label class="form-label">
            Add initial members
            <ui-input
              v-model="memberSearchInput"
              placeholder="Search by username, email, full name"
            />
          </label>

          <div class="member-picker" v-if="memberSearchInput.length > 0">
            <label
              v-for="user in createCandidateUsers"
              :key="`create-${user.id}`"
              class="picker-item"
              @click.prevent="toggleMember(user.id)"
            >
              <input type="checkbox" :checked="form.member_ids.includes(user.id)" readonly />
              <span>{{ user.username }} ({{ user.email }})</span>
            </label>
            <p v-if="createCandidateUsers?.length === 0" class="text-muted empty-note">
              No users found.
            </p>
          </div>
        </div>

        <ui-button class="full-width" :disabled="loading" type="submit">
          {{ loading ? 'Creating...' : 'Create team' }}
        </ui-button>
      </form>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiInput from '@/components/UiInput.vue'
import { useAuth } from '@/composables/useAuth'
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import $api from '@/services'
import type { GetUsersResponse } from '@/services/accounts/types'
import { isApiError } from '@/services/apiClient'
import type { UserId } from '@/services/dbTypes'
import type { CreateTeamBody } from '@/services/teams/types'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const { showNotification, hideNotification } = useGlobalNotification()

type Form = CreateTeamBody

const form = ref<Form>({
  name: '',
  email: '',
  organization: '',
  contact_telegram: '',
  contact_discord: '',
  is_public: false,
  member_ids: [],
})

const resetForm = () => {
  form.value = {
    name: '',
    email: '',
    organization: '',
    contact_telegram: '',
    contact_discord: '',
    is_public: false,
    member_ids: [],
  }
}

const auth = useAuth()

const loading = ref(false)
const memberSearchInput = ref('')
const users = ref<GetUsersResponse | null>(null)

const toggleMember = (id: UserId) => {
  const idx = form.value.member_ids.indexOf(id)
  if (idx === -1) form.value.member_ids.push(id)
  else form.value.member_ids.splice(idx, 1)
}

const createCandidateUsers = computed(() => {
  const search = memberSearchInput.value.trim().toLowerCase()
  return users.value?.filter((user) => {
    if (user.id === auth.user.value?.id) return false
    if (!search) return true
    return [user.username, user.email, user.full_name || '']
      .join(' ')
      .toLowerCase()
      .includes(search)
  })
})

const toggleVisibility = () => {
  form.value.is_public = !form.value.is_public
}

const onVisibilityKeydown = (event: KeyboardEvent) => {
  if (event.key === 'ArrowLeft') {
    event.preventDefault()
    form.value.is_public = false
    return
  }

  if (event.key === 'ArrowRight') {
    event.preventDefault()
    form.value.is_public = true
    return
  }

  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    toggleVisibility()
  }
}

const fetchUsers = async () => {
  try {
    const response = await $api.accounts.getUsers()

    users.value = response.data
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        showNotification('Unable to load users list.', 'error')
      } else {
        showNotification('Unable to connect to server', 'error')
      }
    }
  }
}

const createTeam = async () => {
  loading.value = true
  hideNotification()

  try {
    const response = await $api.teams.createTeam(form.value)

    showNotification('Team created successfully.', 'success')
    resetForm()

    router.push(`/teams/${response.data.id}`)
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        if (err.response.status === 401) return router.push('/login')
        showNotification(err.response.data, 'error')
      } else {
        showNotification('Server connection error.', 'error')
      }
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.teams-page {
  gap: 1.2rem;
}

.back-link {
  display: inline-block;
  margin-bottom: 1rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.full-width {
  grid-column: 1 / -1;
}

.member-picker {
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  background: #fff;
  padding: 0.6rem;
  max-height: 180px;
  overflow: auto;
  display: grid;
  gap: 0.45rem;
}

.toggle-field {
  display: grid;
  gap: 0.45rem;
}

.visibility-control {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
}

.visibility-label {
  color: var(--ink-800);
  font-size: 0.86rem;
  user-select: none;
}

.visibility-switch {
  position: relative;
  display: inline-flex;
  align-items: center;
  width: 3rem;
  height: 1.7rem;
  padding: 0.17rem;
  border: 1px solid var(--line-strong);
  border-radius: 999px;
  background: #fff;
  cursor: pointer;
  flex-shrink: 0;
}

.visibility-switch:focus-visible {
  outline: 2px solid var(--brand-500);
  outline-offset: 2px;
}

.switch-knob {
  width: 1.2rem;
  height: 1.2rem;
  border-radius: 999px;
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  transform: translateX(0);
  transition: transform 180ms ease;
}

.switch-knob.is-public {
  transform: translateX(1.3rem);
}

.picker-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--ink-800);
}

.empty-note {
  margin: 0;
}

@media (max-width: 760px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
