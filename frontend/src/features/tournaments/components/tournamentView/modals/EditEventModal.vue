<template>
  <ui-button size="sm" @click="toggleOpen">Edit</ui-button>

  <ui-modal v-model="isOpen">
    <template #title>
      <h3>Edit event</h3>
    </template>

    <form class="edit-form">
      <label class="form-item">
        <p class="form-label">Title</p>
        <ui-input v-model="titleInput" />
      </label>

      <label class="form-item">
        <p class="form-label">Start Date</p>
        <ui-date-picker v-model="dateInput" />
      </label>

      <label class="form-item">
        <p class="form-label">Start Time</p>
        <ui-time-picker v-model="timeInput" />
      </label>
    </form>

    <template #footer>
      <ui-button variant="secondary" @click="toggleOpen"> Close </ui-button>
      <ui-button> Save </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UiButton from '@/components/UiButton.vue'
import UiDatePicker from '@/components/UiDatePicker.vue'
import UiInput from '@/components/UiInput.vue'
import UiModal from '@/components/UiModal.vue'
import UiTimePicker from '@/components/UiTimePicker.vue'

interface Props {
  eventId: number
  title: string
  startDate: Date
}

const props = defineProps<Props>()

const isOpen = ref(false)
const titleInput = ref(props.title)
const dateInput = ref(new Date(props.startDate))

const pad = (value: number) => String(value).padStart(2, '0')

const timeInput = ref(`${pad(props.startDate.getHours())}:${pad(props.startDate.getMinutes())}`)

const toggleOpen = () => {
  isOpen.value = !isOpen.value
}
</script>

<style scoped>
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
