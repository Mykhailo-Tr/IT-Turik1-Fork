<template>
  <section class="page-shell teams-page">
    <ui-card>
      <template #header>
        <p class="section-eyebrow">Teams</p>
        <h1 class="section-title">Create new team</h1>
        <p class="section-subtitle">Create a team and optionally add initial members.</p>
        <ui-button asLink class="back-link" variant="secondary" size="sm" to="/teams"
          >Back to teams list</ui-button
        >
      </template>

      <form class="form-grid" @submit.prevent="handleFormSubmit">
        <div class="form-item">
          <label class="form-label"> Team name </label>
          <ui-input v-model="form.name" :is-invalid="!!createTeamError?.details.name" required />
          <small v-if="createTeamError?.details.name" class="text-error">{{
            createTeamError?.details.name[0]
          }}</small>
        </div>

        <div class="form-item">
          <label class="form-label"> Team email </label>
          <ui-input
            v-model="form.email"
            :is-invalid="!!createTeamError?.details.email"
            type="email"
            required
          />
          <small v-if="createTeamError?.details.email" class="text-error">{{
            createTeamError?.details.email[0]
          }}</small>
        </div>

        <div class="form-item">
          <label class="form-label"> Organization </label>
          <ui-input
            v-model="form.organization"
            :is-invalid="!!createTeamError?.details.organization"
          />
          <small v-if="createTeamError?.details.organization" class="text-error">{{
            createTeamError?.details.organization[0]
          }}</small>
        </div>

        <label class="form-label toggle-field">
          <span>Team visibility</span>
          <div class="visibility-control">
            <span class="visibility-label">Private</span>
            <ui-switch
              v-model="form.is_public"
              :aria-checked="form.is_public ? 'true' : 'false'"
              :aria-label="`Team visibility: ${form.is_public ? 'Public' : 'Private'}`"
            />
            <span class="visibility-label">Public</span>
          </div>
          <small v-if="createTeamError?.details.is_public" class="text-error">{{
            createTeamError?.details.is_public[0]
          }}</small>
        </label>

        <div class="form-item">
          <label class="form-label"> Telegram </label>
          <ui-input
            v-model="form.contact_telegram"
            :is-invalid="!!createTeamError?.details.contact_telegram"
            placeholder="@team_username"
            pattern="^@?[A-Za-z][A-Za-z0-9_]{4,31}$"
            title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
          />
          <small v-if="createTeamError?.details.contact_telegram" class="text-error">{{
            createTeamError?.details.contact_telegram[0]
          }}</small>
        </div>

        <div class="form-item">
          <label class="form-label"> Discord </label>
          <ui-input
            v-model="form.contact_discord"
            :is-invalid="!!createTeamError?.details.contact_discord"
            placeholder="team.username"
            pattern="^@?(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?$"
            title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
          />
          <small v-if="createTeamError?.details.contact_discord" class="text-error">{{
            createTeamError?.details.contact_discord[0]
          }}</small>
        </div>

        <div class="form-item">
          <label class="form-label"> Add initial members </label>

          <ui-select
            v-model="form.member_ids"
            :isLoading="isLoadingUsers"
            :isError="isLoadingError"
            :error="`Error while fetching users (code: ${getUsersError?.code})`"
            :multiple="true"
            :options="
              createCandidateUsers?.map((u) => ({
                value: u.id,
                label: `${u.username} (${u.email})`,
              }))
            "
            placeholder="Select members"
          />
          <small v-if="createTeamError?.details.member_ids" class="text-error">{{
            createTeamError?.details.member_ids[0]
          }}</small>
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
import { useNotification } from '@/composables/useNotification'
import type { CreateTeamBody } from '@/api/teams/types'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCreateTeam } from '@/queries/teams'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useProfile, useUsers } from '@/queries/accounts'
import UiSelect from '@/components/UiSelect.vue'
import { parseError } from '@/api'
import UiSwitch from '@/components/UiSwitch.vue'

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

const { data: users, isLoading: isLoadingUsers, error: usersError, isLoadingError } = useUsers()
const getUsersError = computed(() => parseError(usersError.value))

const { mutate: createTeam, isPending: isCreatingTeam, error } = useCreateTeam()
const createTeamError = computed(() => parseError(error.value))

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
  font-size: 0.86rem;
  user-select: none;
}

@media (max-width: 760px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
