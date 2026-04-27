<template>
  <ui-button size="sm" variant="danger" @click="isOpen = true">Delete</ui-button>

  <ui-modal v-model="isOpen">
    <template #title>
      <h3>Delete event</h3>
    </template>

    <div>
      <p class="modal-text">
        This action cannot be undone. Enter
        <ui-badge variant="red">{{ props.title }}</ui-badge>
        to confirm deletion.
      </p>

      <ui-input
        v-model="confirmInput"
        :placeholder="props.title"
        style="width: 100%"
        :disabled="isDeleting"
      />

      <p v-if="errorMessage" class="text-error">
        {{ errorMessage }}
      </p>
    </div>

    <template #footer>
      <ui-button variant="secondary" :disabled="isDeleting" @click="closeModal"> Cancel </ui-button>

      <ui-button variant="danger" :disabled="!canDelete" @click="handleDelete">
        Delete permanently
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiBadge from '@/components/ui/UiBadge.vue'

interface Props {
  eventId: number
  title: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'deleted', id: number): void
}>()

const isOpen = ref(false)
const isDeleting = ref(false)
const confirmInput = ref('')
const errorMessage = ref('')

const canDelete = computed(() => {
  return confirmInput.value === props.title && !isDeleting.value
})

function closeModal() {
  isOpen.value = false
  confirmInput.value = ''
  errorMessage.value = ''
}

async function handleDelete() {
  if (!canDelete.value) {
    errorMessage.value = `Please enter "${props.title}" exactly.`
    return
  }

  errorMessage.value = ''
  isDeleting.value = true

  try {
    await new Promise((resolve) => setTimeout(resolve, 1000))

    emit('deleted', props.eventId)
    closeModal()
  } catch {
    errorMessage.value = 'Unable to delete event.'
  } finally {
    isDeleting.value = false
  }
}
</script>

<style scoped>
.modal-text {
  margin-bottom: 1rem;
}

.text-error {
  color: var(--danger);
  margin-top: 0.75rem;
}
</style>
