<script setup lang="ts">
import { computed } from 'vue'

type Size = 'sm' | 'md' | 'lg'

const props = withDefaults(
  defineProps<{
    size?: Size
  }>(),
  {
    size: 'sm',
  },
)

const sizeClass = computed(() => `loader--${props.size ?? 'md'}`)
</script>

<template>
  <svg
    :class="['loader', sizeClass]"
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
  </svg>
</template>

<style scoped>
.loader {
  animation: spin 1s linear infinite;
}

.loader--sm {
  width: 16px;
  height: 16px;
}

.loader--md {
  width: 22px;
  height: 22px;
}

.loader--lg {
  width: 30px;
  height: 30px;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
