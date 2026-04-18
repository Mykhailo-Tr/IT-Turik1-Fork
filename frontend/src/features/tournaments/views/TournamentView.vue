<template>
  <ui-card>
    <template #header>
      <div>
        <p class="section-eyebrow">Tournaments</p>
        <h1>Tournament {{ id }}</h1>
      </div>
    </template>

    <template #footer>
      <ui-button asLink to="/teams/create" variant="secondary" size="sm" class="tournament-link">
        Back to tournaments
      </ui-button>
    </template>
  </ui-card>

  <div class="tournament-grid">
    <TournamentInfo :tournament-id="id" />
    <TournamentTeams :tournament-id="id" />
  </div>
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import { useRoute } from 'vue-router'
import TournamentInfo from '../components/tournamentView/TournamentInfo.vue'

import TournamentTeams from '../components/tournamentView/TournamentTeams.vue'

const route = useRoute()
const id = Number(route.params.id) ?? 1
</script>

<style scoped>
.tournament-link {
  width: max-content;
}

.tournament-grid {
  display: flex;
  gap: 1rem;
  margin-top: 1.2rem;
}

@media (max-width: 810px) {
  .tournament-grid {
    flex-direction: column;
  }
}
</style>
