<template>
  <div :class="['badge', `badge--${props.variant}`]">{{ props.value }}</div>
</template>

<script setup lang="ts">
type Variants = 'green' | 'blue' | 'gray' | 'red' | 'orange'

const props = withDefaults(
  defineProps<{
    value: string
    variant?: Variants
  }>(),
  { variant: 'gray' },
)
</script>

<style scoped>
.badge {
  display: inline-block;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--line-soft);
}

.badge--blue {
  border-color: rgba(14, 116, 144, 0.35);
  background: rgba(14, 116, 144, 0.14);
  color: #0e7490;
}

.badge--green {
  border-color: rgba(20, 184, 166, 0.45);
  background: rgba(20, 184, 166, 0.15);
  color: var(--brand-700);
}

.badge--gray {
  border-color: rgba(15, 23, 42, 0.12);
  background: rgba(15, 23, 42, 0.03);
  color: var(--ink-700);
}

.badge--red {
  border-color: rgba(239, 68, 68, 0.45);
  background: rgba(239, 68, 68, 0.12);
  color: #991b1b;
}

.badge--orange {
  border-color: rgba(245, 158, 11, 0.45);
  background: rgba(245, 158, 11, 0.12);
  color: #92400e;
}
</style>
