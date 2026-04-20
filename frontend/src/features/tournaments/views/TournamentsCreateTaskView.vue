<template>
  <ui-card>
    <template #header>
      <h1>Create round</h1>
    </template>

    <form class="round-form" @submit.prevent="handleSubmit">
      <label class="form-item title-field">
        <span class="form-label">Title</span>
        <ui-input
          v-model="form.fields.value.title"
          placeholder="Enter round title"
          :isInvalid="!!form.errors.value.title"
          @blur="form.validateField('title')"
        />
        <small v-if="form.errors.value.title" class="text-error">{{
          form.errors.value.title
        }}</small>
      </label>

      <label class="form-item desc-field">
        <span class="form-label">Description</span>
        <editor-modal
          v-model="form.fields.value.description"
          title="Description"
          addText="Add description"
          editText="Edit description"
          ariaLabel="Description editor"
          @blur="form.validateField('description')"
        />
        <small v-if="form.errors.value.description" class="text-error">{{
          form.errors.value.description
        }}</small>
      </label>

      <label class="form-item tech-field">
        <span class="form-label">Technical requirements</span>
        <editor-modal
          v-model="form.fields.value.technicalRequirements"
          title="Technical requirements"
          addText="Add technical requirements"
          editText="Edit technical requirements"
          ariaLabel="Technical requirements editor"
          @blur="form.validateField('technicalRequirements')"
        />
        <small v-if="form.errors.value.technicalRequirements" class="text-error">{{
          form.errors.value.technicalRequirements
        }}</small>
      </label>

      <label class="form-item start-date-field">
        <span class="form-label">Start date</span>
        <ui-date-picker
          v-model="form.fields.value.startDate"
          :isInvalid="!!form.errors.value.startDate"
          @blur="form.validateField('startDate')"
        />
        <small v-if="form.errors.value.startDate" class="text-error">{{
          form.errors.value.startDate
        }}</small>
      </label>

      <label class="form-item end-date-field">
        <span class="form-label">End date</span>
        <ui-date-picker
          v-model="form.fields.value.endDate"
          :isInvalid="!!form.errors.value.endDate"
          @blur="form.validateField('endDate')"
        />
        <small v-if="form.errors.value.endDate" class="text-error">{{
          form.errors.value.endDate
        }}</small>
      </label>

      <label class="form-item must-have-field">
        <span class="form-label">Must have</span>
        <editor-modal
          v-model="form.fields.value.mustHave"
          title="Must have"
          addText="Add must have"
          editText="Edit must have"
          ariaLabel="Must have editor"
          @blur="form.validateField('mustHave')"
        />
        <small v-if="form.errors.value.mustHave" class="text-error">{{
          form.errors.value.mustHave
        }}</small>
      </label>

      <ui-button class="submit-btn" type="submit">Create</ui-button>
    </form>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/UiButton.vue'
import UiCard from '@/components/UiCard.vue'
import UiDatePicker from '@/components/UiDatePicker.vue'
import UiInput from '@/components/UiInput.vue'
import EditorModal from '@/features/tournaments/components/createTaskView/modals/EditorModal.vue'
import { useForm } from '@/composables/useForm'
import { CreateRoundSchema } from '@/schemas/tournaments.schema'
import type { JSONContent } from '@tiptap/core'

interface Form {
  title: string
  technicalRequirements: JSONContent | null
  description: JSONContent | null
  mustHave: JSONContent | null
  startDate: Date
  endDate: Date
}

const form = useForm<Form>(CreateRoundSchema, {
  title: '',
  description: null,
  technicalRequirements: null,
  mustHave: null,
  startDate: new Date(),
  endDate: new Date(),
})

function handleSubmit() {
  if (!form.validate()) return

  // TODO: submit to API
  const payload = {
    ...form.fields.value,
  }

  console.log('Create round payload (TipTap JSON):', payload)
}
</script>

<style scoped>
.round-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto auto auto;
  gap: 1rem;
}

.title-field {
  grid-column: 1;
  grid-row: 1;
}

.desc-field {
  grid-column: 1;
  grid-row: 2;
}

.tech-field {
  grid-column: 1;
  grid-row: 3;
}

.must-have-field {
  grid-column: 2;
  grid-row: 3;
}

.start-date-field {
  grid-column: 2;
  grid-row: 1;
}

.end-date-field {
  grid-column: 2;
  grid-row: 2;
}

.submit-btn {
  grid-column: 2;
  grid-row: 4;
  justify-self: end;
}

.text-error {
  color: var(--destructive);
}

@media (max-width: 800px) {
  .round-form {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    gap: 1.2rem;
  }

  .start-date-field,
  .end-date-field,
  .submit-btn {
    grid-column: 1;
    grid-row: auto;
  }
}
</style>
