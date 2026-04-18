<template>
  <ui-card>
    <template #header>
      <h1 class="section-title">Create tournament</h1>
    </template>

    <form class="tournament-form" @submit.prevent="() => {}">
      <label class="form-item name-field">
        <span class="form-label">Team name</span>
        <ui-input
          id="teamName"
          v-model="form.fields.value.name"
          placeholder="Enter tournament name"
          required
          :isInvalid="!!form.errors.value.name"
          @blur="form.validateField('name')"
        />
        <small v-if="form.errors.value.name" class="text-error">{{ form.errors.value.name }}</small>
      </label>

      <label class="form-item description-field">
        <span class="form-label">Description</span>
        <ui-text-area
          id="desc"
          v-model="form.fields.value.description"
          class="description-input"
          required
          :isInvalid="!!form.errors.value.description"
          @blur="form.validateField('description')"
        />
        <small v-if="form.errors.value.description" class="text-error">{{
          form.errors.value.description
        }}</small>
      </label>

      <div class="form-row settings-row">
        <label class="form-item">
          <span class="form-label">Rounds</span>
          <ui-select
            v-model="form.fields.value.rounds"
            :options="[
              { value: '1', label: '1' },
              { value: '2', label: '2' },
              { value: '3', label: '3' },
              { value: '4', label: '4' },
            ]"
            required
            @blur="form.validateField('rounds')"
          />
          <small v-if="form.errors.value.rounds" class="text-error">{{
            form.errors.value.rounds
          }}</small>
        </label>

        <label class="form-item">
          <span class="form-label">Max Teams</span>
          <ui-input
            id="maxTeams"
            type="number"
            v-model.number="form.fields.value.maxTeams"
            min="1"
            max="10"
            required
            :isInvalid="!!form.errors.value.maxTeams"
            @blur="form.validateField('maxTeams')"
          />
          <small v-if="form.errors.value.maxTeams" class="text-error">{{
            form.errors.value.maxTeams
          }}</small>
        </label>
      </div>

      <div class="schedule-column">
        <div class="date-time-group">
          <label class="form-item date-part">
            <span class="form-label">Start date</span>
            <ui-date-picker
              v-model="form.fields.value.startDate"
              required
              @blur="form.validateField('startDate')"
            />
            <small v-if="form.errors.value.startDate" class="text-error">{{
              form.errors.value.startDate
            }}</small>
          </label>

          <label class="form-item time-part">
            <span class="form-label">Time</span>
            <ui-time-picker
              v-model="form.fields.value.startTime"
              class="time-field"
              @blur="form.validateField('startTime')"
            />
            <small v-if="form.errors.value.startTime" class="text-error">{{
              form.errors.value.startTime
            }}</small>
          </label>
        </div>

        <div class="date-time-group">
          <label class="form-item date-part">
            <span class="form-label">End date</span>
            <ui-date-picker
              v-model="form.fields.value.endDate"
              required
              @blur="form.validateField('endDate')"
            />
            <small v-if="form.errors.value.endDate" class="text-error">{{
              form.errors.value.endDate
            }}</small>
          </label>

          <label class="form-item time-part">
            <span class="form-label">Time</span>
            <ui-time-picker
              v-model="form.fields.value.endTime"
              class="time-field"
              @blur="form.validateField('endTime')"
            />
            <small v-if="form.errors.value.endTime" class="text-error">{{
              form.errors.value.endTime
            }}</small>
          </label>
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
import { useForm } from '@/composables/useForm'
import { CreateTournamentSchema } from '@/schemas/tournaments.schema'

interface Form {
  name: string
  description: string
  startDate: Date
  startTime: string
  endTime: string
  endDate: Date
  rounds: number
  maxTeams: number
}

const form = useForm<Form>(CreateTournamentSchema, {
  name: '',
  description: '',
  startDate: new Date(),
  startTime: '00:00',
  endDate: new Date(),
  endTime: '00:00',
  rounds: 1,
  maxTeams: 2,
})
</script>

<style scoped>
.tournament-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto auto;
  gap: 1rem;
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
