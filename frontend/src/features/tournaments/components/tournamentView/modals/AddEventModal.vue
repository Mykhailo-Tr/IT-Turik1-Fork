<template>
  <ui-button @click="open">Add event</ui-button>

  <ui-modal v-model="isOpen">
    <template #title>
      <h3>Create event</h3>
    </template>

    <form class="add-form">
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
      <ui-button variant="secondary" @click="close"> Close </ui-button>

      <ui-button> Save </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UiDatePicker from '@/components/UiDatePicker.vue'
import UiInput from '@/components/UiInput.vue'
import UiModal from '@/components/UiModal.vue'
import UiTimePicker from '@/components/UiTimePicker.vue'
import UiButton from '@/components/UiButton.vue'

interface Props {
  tournamentId: number
}

defineProps<Props>()

const isOpen = ref(false)

const titleInput = ref('')
const dateInput = ref(new Date())
const timeInput = ref('')

function open() {
  isOpen.value = true
}

function close() {
  isOpen.value = false
}
</script>

<style scoped>
.add-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
