<template>
  <article class="card">
    <header v-if="$slots.header">
      <slot name="header" />
    </header>

    <section v-if="$slots.default">
      <slot />
    </section>

    <footer v-if="$slots.footer">
      <slot name="footer" />
    </footer>
  </article>
</template>

<style scoped>
.card {
  border: 1px solid var(--line-soft);
  border-radius: 14px;
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  background: rgba(255, 255, 255, 0.85);
}
</style>
