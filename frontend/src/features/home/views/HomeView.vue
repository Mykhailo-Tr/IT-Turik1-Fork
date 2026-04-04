<template>
  <section class="page-shell home-page">
    <ui-card class="hero">
      <div>
        <p class="eyebrow">Dashboard</p>
        <h1>Welcome back, {{ displayName }}</h1>
        <p class="sub">Manage your profile and stay ready for upcoming competitions.</p>
      </div>

      <ui-button asLink to="/profile" variant="outline" class="open-profile-btn"
        >Open profile</ui-button
      >
    </ui-card>

    <div v-if="error" class="state-box error">{{ error }}</div>

    <div v-else-if="auth.user.value" class="grid">
      <ui-card class="info-card">
        <h2>Account details</h2>
        <p><strong>Username:</strong> {{ auth.user.value!.username }}</p>
        <p><strong>Email:</strong> {{ auth.user.value!.email }}</p>
        <p><strong>Role:</strong> {{ auth.user.value!.role }}</p>
        <p v-if="teamNames"><strong>Teams:</strong> {{ teamNames }}</p>
      </ui-card>

      <ui-card class="info-card accent">
        <h2>Quick status</h2>
        <ul>
          <li>
            Profile ready: <span>{{ profileReady ? 'Yes' : 'No' }}</span>
          </li>
          <li>
            City set: <span>{{ auth.user.value!.city ? 'Yes' : 'No' }}</span>
          </li>
          <li>
            Phone set: <span>{{ auth.user.value!.phone ? 'Yes' : 'No' }}</span>
          </li>
        </ul>
      </ui-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import { useAuth } from '@/composables/useAuth'

const auth = useAuth()

const error = ref('')

const displayName = computed(
  () => auth.user.value?.full_name || auth.user.value?.username || 'User',
)
const profileReady = computed(() => Boolean(auth.user.value?.full_name && auth.user.value?.city))
const teamNames = computed(() => (auth.user.value?.teams || []).map((team) => team.name).join(', '))
</script>

<style scoped>
.home-page {
  display: grid;
  gap: 1rem;
}

.hero {
  padding: 1.4rem;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  background:
    linear-gradient(130deg, rgba(15, 118, 110, 0.95), rgba(20, 184, 166, 0.88)),
    linear-gradient(45deg, rgba(249, 115, 22, 0.2), transparent);
  color: white;
  border: none;
}

.eyebrow {
  margin: 0;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.75rem;
  opacity: 0.85;
}

h1 {
  margin: 0.45rem 0 0;
  font-family: var(--font-display);
  font-size: clamp(1.4rem, 1.3vw + 1rem, 2rem);
}

.sub {
  margin: 0.5rem 0 0;
  opacity: 0.92;
}

.hero-actions {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.open-profile-btn {
  color: white;
  border-color: white;
}

.state-box {
  border-radius: 16px;
  padding: 1rem 1.1rem;
  border: 1px solid var(--line-soft);
  background: var(--surface-strong);
}

.state-box.error {
  border-color: rgba(220, 38, 38, 0.25);
  color: #b91c1c;
  background: rgba(254, 242, 242, 0.9);
}

.grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.info-card {
  padding: 1.2rem;
}

.info-card h2 {
  margin-top: 0;
  font-family: var(--font-display);
}

.info-card p {
  margin: 0.5rem 0;
  color: var(--ink-700);
}

.accent {
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.92), rgba(237, 254, 255, 0.95));
}

ul {
  margin: 0.8rem 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.55rem;
}

li {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px dashed var(--line-soft);
  padding-bottom: 0.35rem;
}

li span {
  font-weight: 700;
}

@media (max-width: 760px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-actions {
    justify-content: flex-start;
  }

  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
