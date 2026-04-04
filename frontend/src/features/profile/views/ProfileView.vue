<template>
  <section class="page-shell">
    <ui-card class="profile-card">
      <div class="head">
        <div>
          <p class="section-eyebrow">User Center</p>
          <h1 class="section-title profile-title">My profile</h1>
        </div>
        <p class="meta">
          Joined: {{ auth.user.value?.created_at ? formatDate(auth.user.value.created_at) : 'N/A' }}
        </p>
      </div>

      <div v-if="auth.isLoading.value" class="state-box">Loading profile...</div>
      <div v-else class="details">
        <ui-card class="item-text" title="Username">
          <strong class="item-value value-wrap">{{ auth.user.value?.username || '-' }}</strong>
        </ui-card>
        <ui-card class="item-text" title="Email">
          <strong class="item-value value-wrap">{{ auth.user.value?.email || '-' }}</strong>
        </ui-card>
        <ui-card class="item-role" title="Role">
          <ui-badge variant="green">{{ auth.user.value?.role ?? '-' }}</ui-badge>
        </ui-card>
        <ui-card class="item-text" title="Full name">
          <strong class="item-value value-wrap">{{ auth.user.value?.full_name || '-' }}</strong>
        </ui-card>
        <ui-card class="item-text" title="City">
          <strong class="item-value value-wrap">{{ auth.user.value?.city || '-' }}</strong>
        </ui-card>
        <ui-card class="item-phone" title="phone">
          <strong class="item-value value-fixed">{{ auth.user.value?.phone || '-' }}</strong>
        </ui-card>
        <ui-card class="item-wide">
          <span class="item-label">Teams</span>
          <div class="team-list">
            <router-link
              v-for="team in auth.user.value?.teams || []"
              :key="team.id"
              :to="`/teams/${team.id}`"
              class="team-link"
            >
              {{ team.name }}
            </router-link>
            <p v-if="!(auth.user.value?.teams || []).length" class="text-muted">No teams yet.</p>
          </div>
        </ui-card>
      </div>

      <div class="actions">
        <ui-button :disabled="auth.isLoading.value" @click="goToEditProfile">
          Edit Profile
        </ui-button>
        <ui-button
          variant="outline"
          :disabled="auth.isLoading.value || isDeleting"
          @click="auth.logout()"
        >
          Log Out
        </ui-button>
      </div>

      <div class="danger-zone">
        <p class="danger-text">Danger zone: this action permanently deletes your account.</p>

        <delete-profile-modal />
      </div>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiBadge from '@/components/UiBadge.vue'
import { useAuth } from '@/composables/useAuth'
import DeleteProfileModal from '../components/modals/DeleteProfileModal.vue'

const auth = useAuth()
const router = useRouter()
const isDeleting = ref(false)

const goToEditProfile = () => {
  router.push('/profile/edit')
}

const formatDate = (date: Date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('uk-UA')
}
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

.details {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.6rem;
  margin-top: 1rem;
  align-items: start;
}

.item {
  border: 1px solid var(--line-soft);
  border-radius: 14px;
  padding: 0.7rem;
  background: rgba(255, 255, 255, 0.85);
  min-width: 0;
  display: grid;
  gap: 0.3rem;
  align-content: start;
}

.item-label {
  color: var(--ink-500);
  font-size: 0.8rem;
  font-weight: 600;
  line-height: 1.2;
}

.item-role,
.item-phone,
.item-text {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.item-phone {
  align-content: start;
}

.item-wide {
  grid-column: 1 / -1;
}

.team-list {
  margin-top: 0.4rem;
  display: grid;
  gap: 0.35rem;
  min-width: 0;
}

.team-link {
  color: var(--brand-700);
  text-decoration: none;
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
  border-top: 1px dashed var(--line-strong);
  padding-top: 1rem;
}

.danger-text {
  margin: 0 0 0.6rem;
  color: #991b1b;
  font-weight: 600;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: grid;
  place-items: center;
  z-index: 50;
  padding: 1rem;
}

.btn-cancel {
  border: 1px solid var(--line-strong);
  border-radius: 12px;
  padding: 0.7rem 1rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
  background: #fff;
}

.btn-cancel:disabled {
  opacity: 0.65;
  cursor: not-allowed;
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
