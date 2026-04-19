<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div>
          <p class="section-eyebrow">Tournaments</p>
          <h1>Tournament {{ id }}</h1>
        </div>
      </template>

      <template #footer>
        <ui-button asLink to="/tournaments" variant="secondary" size="sm" class="tournament-link">
          Back to tournaments
        </ui-button>
      </template>
    </ui-card>

    <ui-card>
      <div class="sections">
        <ui-button
          variant="secondary"
          :class="['sections-btn', { active: currentSection === 'information' }]"
          @click="setActiveSection('information')"
          >Information</ui-button
        >
        <ui-button
          variant="secondary"
          :class="['sections-btn', { active: currentSection === 'rounds' }]"
          @click="setActiveSection('rounds')"
          >Rounds</ui-button
        >
        <ui-button
          variant="secondary"
          :class="['sections-btn', { active: currentSection === 'submissions' }]"
          @click="setActiveSection('submissions')"
          >Submissions</ui-button
        >
        <ui-button
          variant="secondary"
          :class="['sections-btn', { active: currentSection === 'schedule' }]"
          @click="setActiveSection('schedule')"
          >Schedule</ui-button
        >
        <ui-button
          variant="secondary"
          :class="['sections-btn', { active: currentSection === 'leaderboard' }]"
          @click="setActiveSection('leaderboard')"
          >Leaderboard</ui-button
        >
      </div>
    </ui-card>

    <div class="tournament-grid" v-if="currentSection === 'information'">
      <TournamentInfo :tournament-id="id" />
      <TournamentTeams :tournament-id="id" />
    </div>

    <TournamentRounds :tournament-id="id" v-if="currentSection === 'rounds'" />

    <TournamentSchedule :tournament-id="id" v-if="currentSection === 'schedule'" />
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import { useRoute } from 'vue-router'
import TournamentInfo from '../components/tournamentView/TournamentInfo.vue'
import TournamentTeams from '../components/tournamentView/TournamentTeams.vue'
import { ref } from 'vue'
import TournamentSchedule from '../components/tournamentView/TournamentSchedule.vue'
import TournamentRounds from '../components/tournamentView/TournamentRounds.vue'

type Sections = 'information' | 'schedule' | 'rounds' | 'submissions' | 'leaderboard'

const route = useRoute()
const id = Number(route.params.id) ?? 1

const currentSection = ref<Sections>('information')

const setActiveSection = (section: Sections) => {
  currentSection.value = section
}
</script>

<style scoped>
.tournament-link {
  width: max-content;
}

.sections {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.sections-btn.active {
  background: var(--primary);
  color: var(--primary-foreground);
}

.tournament-grid {
  display: flex;
  gap: 1rem;
}

@media (max-width: 810px) {
  .tournament-grid {
    flex-direction: column;
  }
}
</style>
