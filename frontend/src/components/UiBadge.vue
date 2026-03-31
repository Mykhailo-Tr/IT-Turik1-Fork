<template>
  <div :class="['badge', `badge--${props.variant}`]">{{ props.value }}</div>
</template>

<script setup lang="ts">
type Variants = 'green' | 'blue'

const props = defineProps<{
  value: string
  variant: Variants
}>()
</script>

<style scoped>
.badge {
  display: inline-block;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 700;
}

.badge--blue {
  border: 1px solid rgba(14, 116, 144, 0.35);
  background: rgba(14, 116, 144, 0.14);
  color: #0e7490;
  padding: 0.2rem 0.5rem;
}

.badge--green {
  border: 1px solid rgba(20, 184, 166, 0.45);
  background: rgba(20, 184, 166, 0.15);
  color: var(--brand-700);
  padding: 0.2rem 0.55rem;
}
</style>
