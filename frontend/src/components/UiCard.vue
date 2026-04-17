<template>
  <div class="card">
    <slot v-if="$slots.header" name="header" />

    <Transition name="error-fade" role="alert">
      <div v-if="props.isError">
        <slot name="error" />
      </div>
    </Transition>

    <slot v-if="!props.isError && $slots.default" />

    <slot v-if="$slots.footer" name="footer" />
  </div>
</template>

<script setup lang="ts">
interface Props {
  isError?: boolean
}

const props = defineProps<Props>()
</script>

<style scoped>
.card {
  border: 1px solid;
  border-color: inherit;
  border-radius: 14px;
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: var(--card);
  color: var(--card-foreground);
}

.error-fade-enter-active,
.error-fade-leave-active {
  transition: opacity 0.15s ease;
}

.error-fade-enter-from,
.error-fade-leave-to {
  opacity: 0;
}
</style>
