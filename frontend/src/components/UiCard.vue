<template>
  <div class="card">
    <span v-if="props.title" class="card-title">{{ title }}</span>
    <slot />
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
}

const props = defineProps<Props>()
</script>

<style scoped>
.card {
  border: 1px solid var(--line-soft);
  border-radius: 14px;
  padding: 1.2rem;
  background: rgba(255, 255, 255, 0.85);
}

.card-title {
  color: var(--ink-500);
  font-size: 0.8rem;
  font-weight: 600;
  line-height: 1.2;
}
</style>
