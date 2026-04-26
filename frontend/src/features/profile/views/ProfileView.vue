<template>
  <section class="page-shell">
    <ui-card :is-error="isLoadingError">
      <template #error>
        <div style="display: flex; height: 436px; justify-content: center; align-items: center">
          <p>Error while fetching profile info (code: {{ error?.code }})</p>
        </div>
      </template>

      <template #header>
        <div>
          <div class="top-header">
            <p class="section-eyebrow">User Center</p>
            <p class="meta">
              Joined: {{ user?.created_at ? formatDate(user?.created_at) : 'N/A' }}
            </p>
          </div>
          <h1 class="section-title">My profile</h1>
        </div>
      </template>

      <div>
        <div class="details">
          <ui-card class="field-card">
            <template #header>
              <span class="card-text-title">Username</span>
            </template>

            <ui-skeleton-loader :loading="isLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" width="100%" />
              </template>

              <strong class="card-content">{{ user?.username || '-' }}</strong>
            </ui-skeleton-loader>
          </ui-card>

          <ui-card class="field-card">
            <template #header>
              <span class="card-text-title">Email</span>
            </template>

            <ui-skeleton-loader :loading="isLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" width="100%" />
              </template>

              <strong class="card-content">{{ user?.email || '-' }}</strong>
            </ui-skeleton-loader>
          </ui-card>

          <ui-card class="field-card">
            <template #header>
              <span class="card-text-title">Role</span>
            </template>

            <ui-skeleton-loader :loading="isLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" width="100%" />
              </template>

              <ui-badge variant="primary">{{ user?.role ?? '-' }}</ui-badge>
            </ui-skeleton-loader>
          </ui-card>

          <ui-card class="field-card">
            <template #header>
              <span class="card-text-title">Full name</span>
            </template>

            <ui-skeleton-loader :loading="isLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" width="100%" />
              </template>

              <strong class="card-content">{{ user?.full_name || '-' }}</strong>
            </ui-skeleton-loader>
          </ui-card>

          <ui-card class="field-card">
            <template #header>
              <span class="card-text-title">City</span>
            </template>

            <ui-skeleton-loader :loading="isLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" width="100%" />
              </template>

              <strong class="card-content">{{ user?.city || '-' }}</strong>
            </ui-skeleton-loader>
          </ui-card>

          <ui-card class="field-card">
            <template #header>
              <span class="card-text-title">Phone</span>
            </template>

            <ui-skeleton-loader :loading="isLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" width="100%" />
              </template>

              <strong class="card-content">{{ user?.phone || '-' }}</strong>
            </ui-skeleton-loader>
          </ui-card>

          <ui-card class="field-card">
            <template #header>
              <span class="card-text-title">Teams</span>
            </template>

            <div>
              <ui-skeleton-loader :loading="isLoading">
                <template #skeleton>
                  <div style="display: flex; flex-direction: column; gap: 4px">
                    <ui-skeleton v-for="i in 2" :key="i" variant="rect" width="150px" />
                  </div>
                </template>

                <div class="team-list">
                  <router-link
                    v-for="team in user?.teams || []"
                    :key="team.id"
                    :to="`/teams/${team.id}`"
                    :title="team.name"
                    class="team-link"
                  >
                    {{ truncateText(team.name, 20) }}
                  </router-link>
                </div>

                <p v-if="!(user?.teams || []).length" class="text-muted">No teams yet.</p>
              </ui-skeleton-loader>
            </div>
          </ui-card>
        </div>

        <div class="actions">
          <ui-button :disabled="isLoading" @click="goToEditProfile"> Edit Profile </ui-button>
          <ui-button variant="secondary" :disabled="isLoading || isDeleting" @click="logout">
            Log Out
          </ui-button>
        </div>
      </div>

      <template #footer>
        <ui-card class="danger-zone">
          <div>
            <p class="danger-text">Danger zone: this action permanently deletes your account.</p>

            <delete-profile-modal />
          </div>
        </ui-card>
      </template>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiBadge from '@/components/UiBadge.vue'
import DeleteProfileModal from '../components/modals/DeleteProfileModal.vue'
import { useProfile } from '@/queries/accounts'
import { useUserStore } from '@/stores/user'
import UiSkeletonLoader from '@/components/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/UiSkeleton.vue'
import { parseApiError } from '@/api'
import { truncateText } from '@/lib/utils'

const store = useUserStore()
const { data: user, isLoading, isLoadingError, error: profileError } = useProfile()
const error = computed(() => parseApiError(profileError.value))

const router = useRouter()
const isDeleting = ref(false)

const logout = () => {
  store.logout()
  router.push('/login')
}

const goToEditProfile = () => {
  router.push('/profile/edit')
}

const formatDate = (date: Date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('uk-UA')
}
</script>

<style scoped>
.meta {
  margin: 0;
  font-size: 0.86rem;
}

.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.details {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.6rem;
  align-items: start;
}

.field-card {
  background: var(--muted);
  gap: 5px;
}

.card-text-title {
  font-size: 0.8rem;
  font-weight: 600;
  line-height: 1.2;
}

.card-content {
  color: var(--muted-foreground);
}

.team-list {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.team-link {
  color: var(--brand-700);
  font-weight: 700;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.badge {
  width: max-content;
  text-transform: uppercase;
}

.actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.danger-zone {
  margin-top: 1.4rem;
  padding-top: 1rem;
  border: 1px solid color-mix(in srgb, var(--destructive) 20%, transparent);
  background: color-mix(in srgb, var(--destructive) 10%, transparent);
}

.danger-text {
  margin: 0 0 0.6rem;
  color: color-mix(in srgb, var(--destructive) 80%, transparent);
  font-weight: 600;
}

@media (max-width: 760px) {
  .profile-card {
    max-width: 100%;
    margin: 0;
  }

  .head {
    flex-direction: column;
    align-items: flex-start;
  }

  .details {
    grid-template-columns: 1fr;
  }

  .actions {
    flex-direction: column;
  }
}
</style>
