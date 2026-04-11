<template>
  <section class="page-shell centered">
    <ui-card class="register-card">
      <p class="section-eyebrow">Join the Platform</p>
      <h1 class="section-title">Create your account</h1>
      <p class="section-subtitle">Get access to tournaments, team tools, and profile management.</p>

      <div v-if="isSuccess" class="notice success">
        Registration completed. Check <strong>{{ form.email }}</strong> to activate your account.
      </div>

      <form v-else @submit.prevent="handleRegister" class="register-form">
        <div class="form-grid">
          <div class="form-item">
            <label class="form-label"> Username </label>
            <ui-input
              v-model="form.username"
              :is-invalid="!!error?.details.username"
              placeholder="johndoe"
              required
            />
            <small v-if="error?.details.username" class="text-error">{{
              error?.details.username[0]
            }}</small>
          </div>

          <div class="form-item">
            <label class="form-label"> Email </label>
            <ui-input
              v-model="form.email"
              :is-invalid="!!error?.details.email"
              placeholder="name@mail.com"
              required
            />
            <small v-if="error?.details.email" class="text-error">{{
              error?.details.email[0]
            }}</small>
          </div>

          <div class="form-item">
            <label class="form-label"> Password </label>
            <ui-password-field
              v-model="form.password"
              autocomplete="new-password"
              :is-invalid="!!error?.details.password"
              placeholder="********"
              required
            />
            <small v-if="error?.details.password" class="text-error">{{
              error?.details.password[0]
            }}</small>
          </div>

          <div class="form-item">
            <label class="form-label"> Role </label>
            <ui-select
              :options="[
                { value: 'team', label: 'Team Member' },
                { value: 'organizer', label: 'Organizer' },
                { value: 'jury', label: 'Jury' },
                { value: 'admin', label: 'Admin' },
              ]"
              v-model="form.role"
              class="select-control"
            />
          </div>
        </div>

        <div class="form-item" v-if="isRestrictedRole">
          <label class="form-label full-width"> Redeem code </label>
          <ui-input
            v-model="form.redeem_code"
            :is-invalid="!!error?.details.redeem_code"
            placeholder="Enter one-time activation code"
            required
          />
          <small v-if="error?.details.redeem_code" class="text-error">{{
            error?.details.redeem_code[0]
          }}</small>
        </div>

        <div style="display: flex; flex-direction: column; gap: 0.9rem">
          <div class="form-item">
            <label class="form-label full-width"> Full name </label>
            <ui-input
              v-model="form.full_name"
              :is-invalid="!!error?.details.full_name"
              placeholder="John Doe"
            />
            <small v-if="error?.details.full_name" class="text-error">{{
              error?.details.full_name[0]
            }}</small>
          </div>

          <div class="form-grid">
            <div class="form-item">
              <label class="form-label"> Phone </label>
              <PhoneField
                v-model="form.phone"
                :error="error?.details.username?.[0]"
                placeholder="Enter phone number"
              />
            </div>

            <div class="form-item">
              <label class="form-label"> City </label>
              <ui-input
                v-model="form.city"
                :is-invalid="!!error?.details.city"
                placeholder="Kyiv"
              />
              <small v-if="error?.details.city" class="text-error">{{
                error?.details.city[0]
              }}</small>
            </div>
          </div>
        </div>

        <ui-button type="submit" class="submit-btn" :disabled="isLoading">
          {{ isLoading ? 'Creating account...' : 'Create account' }}
        </ui-button>

        <GoogleAuthButton divider-label="or sign up with" @success="saveTokensAndRedirect" />

        <p class="auth-link">
          Already have an account?
          <router-link to="/login">Sign in</router-link>
        </p>
      </form>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import GoogleAuthButton from '@/components/shared/GoogleAuthButton.vue'
import UiPasswordField from '@/components/UiPasswordField.vue'
import PhoneField from '@/components/shared/PhoneField.vue'
import type { RegisterResponse } from '@/api/accounts/types'
import UiButton from '@/components/UiButton.vue'
import UiInput from '@/components/UiInput.vue'
import UiSelect from '@/components/UiSelect.vue'
import UiCard from '@/components/UiCard.vue'
import { useRegister } from '@/queries/accounts'
import type { UserRole } from '@/api/dbTypes'
import { useNotification } from '@/composables/useNotification'
import { useUserStore } from '@/stores/user'
import { parseError } from '@/api'

const router = useRouter()

interface Form {
  username: string
  full_name: string
  email: string
  password: string
  role: UserRole
  redeem_code: string
  phone: string
  city: string
}

const form = ref<Form>({
  username: '',
  email: '',
  password: '',
  role: 'team',
  redeem_code: '',
  full_name: '',
  phone: '',
  city: '',
})

const restrictedRoles = ['jury', 'organizer', 'admin']
const isRestrictedRole = computed(() => restrictedRoles.includes(form.value.role))

watch(
  () => form.value.role,
  (newRole) => {
    if (!restrictedRoles.includes(newRole)) {
      form.value.redeem_code = ''
    }
  },
)

const { showNotification } = useNotification()
const storage = useUserStore()

const saveTokensAndRedirect = (data: RegisterResponse) => {
  storage.setTokens(data)
  router.push('/')
}

const { mutate: register, isPending: isLoading, isSuccess, error: registerError } = useRegister()
const error = computed(() => parseError(registerError.value))

const handleRegister = () => {
  register(
    { body: form.value },
    {
      onError: (err) => {
        showNotification(parseError(err)?.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
.register-card {
  width: min(100%, 720px);
  padding: 2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
  margin-bottom: 0.9rem;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.full-width {
  grid-column: 1 / -1;
}

.submit-btn {
  width: 100%;
  margin-top: 1rem;
}

@media (max-width: 760px) {
  .register-card {
    padding: 1.3rem;
    border-radius: 18px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
