<template>
  <section class="page-shell teams-page">
    <ui-card class="create-card">
      <p class="section-eyebrow">Teams</p>
      <h1 class="section-title">Create new team</h1>
      <p class="section-subtitle">Create a team and optionally add initial members.</p>
      <ui-button asLink class="back-link" variant="outline" size="sm" to="/teams"
        >Back to teams list</ui-button
      >

      <form class="form-grid" @submit.prevent="handleCreateTeam">
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

          <div class="member-picker">
            <label
              v-for="user in createCandidateUsers"
              :key="`create-${user.id}`"
              class="picker-item"
            >
              <ui-input v-model="form.member_ids" type="checkbox" :value="user.id" />
              <span>{{ user.username }} ({{ user.email }})</span>
            </label>
            <p v-if="createCandidateUsers.length === 0" class="text-muted empty-note">
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
import { useGlobalNotification } from '@/features/shared/lib/notifications'
import $api from '@/services'
import type { GetUsersResponse } from '@/services/accounts'
import { isApiError } from '@/services/apiClient'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const { showNotification, hideNotification } = useGlobalNotification()

const form = ref({
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

const loading = ref(false)
const memberSearchInput = ref('')
const users = ref<GetUsersResponse>([])
const currentUserId = ref<number | null>(null)

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

const createCandidateUsers = computed(() => {
  const search = memberSearchInput.value.trim().toLowerCase()
  return users.value.filter((user) => {
    if (user.id === currentUserId.value) return false
    if (!search) return true
    return [user.username, user.email, user.full_name || '']
      .join(' ')
      .toLowerCase()
      .includes(search)
  })
})

const handleCreateTeam = async () => {
  loading.value = true
  hideNotification()

  const token = localStorage.getItem('access')
  if (!token) return router.push('/login')

  try {
    const response = await $api.accounts.createTeam(token, form.value)

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
</script>

<style scoped src="../styles/teams-create-view.css"></style>
<style scoped src="../styles/status-tags.css"></style>
