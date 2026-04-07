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

const props = defineProps({
  variant: {
    type: String as () => 'circle' | 'rect',
    default: 'text',
  },
  width: {
    type: [String, Number],
    default: '100%',
  },
  height: {
    type: [String, Number],
    default: '24px',
  },
})

const styleVars = computed(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width,
  height: typeof props.height === 'number' ? `${props.height}px` : props.height,
}))

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

.skeleton--circle {
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
