<template>
  <ui-card>
    <template #header>
      <h1 class="section-title">Create tournament</h1>
    </template>

    <form class="tournament-form" @submit.prevent="() => {}">
      <div class="form-item name-field">
        <label class="form-label">Team name</label>
        <ui-input v-model="createForm.name" required />
      </div>

      <div class="form-item description-field">
        <label class="form-label">Description</label>
        <ui-text-area v-model="createForm.description" class="description-input" required />
      </div>

      <div class="form-row settings-row">
        <div class="form-item">
          <label class="form-label">Rounds</label>
          <ui-select
            v-model="createForm.rounds"
            :options="[
              { value: '1', label: '1' },
              { value: '2', label: '2' },
              { value: '3', label: '3' },
              { value: '4', label: '4' },
            ]"
            required
          />
        </div>
        <div class="form-item">
          <label class="form-label">Max Teams</label>
          <ui-input v-model="createForm.maxTeams" type="number" min="1" max="10" required />
        </div>
      </div>

      <div class="schedule-column">
        <div class="date-time-group">
          <div class="form-item date-part">
            <label class="form-label">Start date</label>
            <ui-date-picker v-model="createForm.startDate" required />
          </div>
          <div class="form-item time-part">
            <label class="form-label form-time">Time</label>
            <ui-time-picker v-model="createForm.startTime" class="time-field" />
          </div>
        </div>

        <div class="date-time-group">
          <div class="form-item date-part">
            <label class="form-label">End date</label>
            <ui-date-picker v-model="createForm.endDate" required />
          </div>
          <div class="form-item time-part">
            <label class="form-label form-time">Time</label>
            <ui-time-picker v-model="createForm.endTime" class="time-field" />
          </div>
        </div>
      </div>

      <ui-button type="submit">Create</ui-button>
    </form>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiDatePicker from '@/components/UiDatePicker.vue'
import UiInput from '@/components/UiInput.vue'
import UiSelect from '@/components/UiSelect.vue'
import UiTextArea from '@/components/UiTextArea.vue'
import UiTimePicker from '@/components/UiTimePicker.vue'
import { reactive } from 'vue'

interface CreateForm {
  name: string
  description: string
  startDate: Date
  startTime: string
  endDate: Date
  endTime: string
  rounds: String
  maxTeams: string
}

const createForm = reactive<CreateForm>({
  name: '',
  description: '',
  startDate: new Date(),
  startTime: '',
  endDate: new Date(),
  endTime: '',
  rounds: '1',
  maxTeams: '2',
})
</script>

<style scoped>
.tournament-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto auto;
  gap: 1rem;
  margin-bottom: 2rem;
}

.name-field {
  grid-column: 1;
  grid-row: 1;
}

.description-field {
  grid-column: 2;
  grid-row: 1 / 4;
}

.description-input {
  height: 100%;
}

.settings-row {
  grid-column: 1;
  grid-row: 2;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.8rem;
}

.schedule-column {
  grid-column: 1;
  grid-row: 3;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.date-time-group {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 0.8rem;
}

.time-field {
  width: 100%;
}

@media (max-width: 800px) {
  .tournament-form {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    gap: 1.2rem;
  }

  .name-field,
  .description-field,
  .settings-row,
  .schedule-column {
    grid-column: 1;
    grid-row: auto;
  }

  .description-input {
    height: 150px;
  }
}

@media (max-width: 480px) {
  .date-time-group {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .settings-row {
    grid-template-columns: 1fr;
  }
}
</style>
