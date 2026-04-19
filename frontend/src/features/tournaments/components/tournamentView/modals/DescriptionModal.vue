<template>
  <p :title="props.description" @click="toggleDescriptionModal">
    {{ truncateText(props.description, 190) }}
    <full-screen-icon
      class="text-muted"
      width="15px"
      height="15px"
      style="display: inline; margin-left: 4px"
    />
  </p>

  <ui-modal v-model="isDescriptionModalOpen">
    <template #title>
      <h3>Tournament description</h3>
    </template>

    <p class="text-muted">
      {{ props.description }}
    </p>
  </ui-modal>
</template>

<script setup lang="ts">
import UiModal from '@/components/UiModal.vue'
import FullScreenIcon from '@/icons/FullScreenIcon.vue'
import { truncateText } from '@/lib/utils'
import { ref } from 'vue'

interface Props {
  description: string
}

const props = defineProps<Props>()

const isDescriptionModalOpen = ref(false)

const toggleDescriptionModal = () => {
  isDescriptionModalOpen.value = !isDescriptionModalOpen.value
}
</script>
