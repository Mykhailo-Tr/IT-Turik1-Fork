<template>
  <section class="page-shell teams-page">
    <ui-card>
      <template #header>
        <p class="section-eyebrow">Teams</p>
        <h1 class="section-title">Create new team</h1>
        <p class="section-subtitle">Create a team and optionally add initial members.</p>
        <ui-button asLink class="back-link" variant="outline" size="sm" to="/teams"
          >Back to teams list</ui-button
        >
      </template>

      <form class="form-grid" @submit.prevent="handleFormSubmit">
        <div class="form-item">
          <label class="form-label"> Team name </label>
          <ui-input v-model="form.name" required />
        </div>

        <div class="form-item">
          <label class="form-label"> Team email </label>
          <ui-input v-model="form.email" type="email" required />
        </div>

        <div class="form-item">
          <label class="form-label"> Organization </label>
          <ui-input v-model="form.organization" />
        </div>

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

        <div class="form-item">
          <label class="form-label"> Telegram </label>
          <ui-input
            v-model="form.contact_telegram"
            placeholder="@team_username"
            pattern="^@?[A-Za-z][A-Za-z0-9_]{4,31}$"
            title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
          />
        </div>

        <div class="form-item">
          <label class="form-label"> Discord </label>
          <ui-input
            v-model="form.contact_discord"
            placeholder="team.username"
            pattern="^@?(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?$"
            title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
          />
        </div>

        <div class="full-width">
          <label class="form-label"> Add initial members </label>

          <ui-skeleton-loader :loading="isLoadingUsers">
            <template #skeleton>
              <ui-skeleton variant="rect" height="48px" width="200px" />
            </template>

            <ui-select
              v-model="form.member_ids"
              :multiple="true"
              :options="
                createCandidateUsers?.map((u) => ({
                  value: u.id,
                  label: `${u.username} (${u.email})`,
                }))
              "
              placeholder="Select members"
            />
          </ui-skeleton-loader>
        </div>

        <ui-button class="full-width" :disabled="isCreatingTeam" type="submit">
          <loading-icon v-if="isCreatingTeam" />
          Create team
        </ui-button>
      </form>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiInput from '@/components/UiInput.vue'
import { useNotification } from '@/features/shared/composables/useNotification'
import type { CreateTeamBody } from '@/api/teams/types'
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCreateTeam } from '@/queries/teams'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useProfile, useUsers } from '@/queries/accounts'
import UiSkeletonLoader from '@/components/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/UiSkeleton.vue'
import UiSelect from '@/components/UiSelect.vue'

const router = useRouter()
const { showNotification, hideNotification } = useNotification()

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

const { data: user } = useProfile()

const createCandidateUsers = computed(() => {
  return users.value?.filter((u) => {
    if (u.id === user.value?.id) return false
    return [u.username, u.email, u.full_name || ''].join(' ').toLowerCase()
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

const { data: users, isLoading: isLoadingUsers, error } = useUsers()

watch(error, (err) => {
  if (err) {
    showNotification(
      err.response ? 'Unable to load users list.' : 'Unable to connect to server.',
      'error',
    )
  }
})

const { mutate: createTeam, isPending: isCreatingTeam } = useCreateTeam()

const handleFormSubmit = () => {
  hideNotification()

  createTeam(
    { body: form.value },
    {
      onSuccess: (data) => {
        showNotification('Team created successfully.', 'success')
        resetForm()

        router.push(`/teams/${data.id}`)
      },
    },
  )
}
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

.form-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.full-width {
  grid-column: 1 / -1;
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

@media (max-width: 760px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
