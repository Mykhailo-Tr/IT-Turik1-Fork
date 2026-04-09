<template>
  <div
    aria-busy="true"
    aria-live="polite"
    aria-label="loading"
    :class="['skeleton', 'animated', variantClass]"
    :style="styleVars"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

export type Variant = 'rect' | 'rounded'

interface Props {
  variant?: Variant
  width?: string | number
  height?: string | number
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'rect',
  width: '100%',
  height: '24px',
})

const styleVars = computed(() => {
  const width = typeof props.width === 'number' ? `${props.width}px` : props.width
  const height = typeof props.height === 'number' ? `${props.height}px` : props.height

  return { width, height }
})

const variantClass = computed(() => `skeleton--${props.variant}`)
</script>

<style scoped>
.skeleton {
  background: linear-gradient(
    90deg,
    rgba(224, 224, 224, 0.7) 0%,
    rgba(245, 245, 245, 0.9) 50%,
    rgba(224, 224, 224, 0.7) 100%
  );
  background-size: 200% 100%;
  border-radius: 4px;
}

.skeleton.animated {
  animation: shimmer 2s infinite linear;
}

.skeleton--rounded {
  border-radius: 50%;
}

.skeleton--rect {
  border-radius: 8px;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
