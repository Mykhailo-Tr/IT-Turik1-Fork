<template>
  <div :style="{ minHeight: containerHeight }">
    <Transition name="skeleton-fade" mode="out-in">
      <div v-if="loading" key="skeleton" class="skeleton-slot">
        <slot name="skeleton" />
      </div>

      <div v-else key="content" class="content-slot">
        <slot />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  loading: boolean
  minHeight?: string
  minWidth?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: true,
})

const containerHeight = computed(() => props.minHeight)
</script>

<style scoped>
.skeleton-slot,
.content-slot {
  width: 100%;
}

.skeleton-fade-enter-active {
  transition: opacity 0.4s ease;
}

.skeleton-fade-leave-active {
  transition: opacity 0.1s ease;
}

.skeleton-fade-enter-from {
  opacity: 0;
}

.skeleton-fade-leave-to {
  opacity: 0;
}
</style>
