<template>
  <article class="card">
    <header v-if="$slots.header">
      <slot name="header" />
    </header>

    <Transition name="error-fade" role="alert">
      <slot name="error" v-if="props.isError" />
    </Transition>

    <template v-if="!props.isError">
      <section v-if="$slots.default">
        <slot />
      </section>
    </template>

    <footer v-if="$slots.footer">
      <slot name="footer" />
    </footer>
  </article>
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
  gap: 0.5rem;
  background: var(--card);
  color: var(--card-foreground);
}

.error-fade-enter-active {
  transition: opacity 0.2s ease;
}

.error-fade-leave-active {
  transition: opacity 0.1s ease;
}

.error-fade-enter-from {
  opacity: 0;
}

.error-fade-leave-to {
  opacity: 0;
}
</style>
