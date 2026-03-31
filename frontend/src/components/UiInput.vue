<template>
  <input class="input" type="text" :value="modelValue" @input="handleInput" />
</template>

<script setup lang="ts">
defineProps({ modelValue: { type: String, default: '' } })
const emit = defineEmits(['update:modelValue'])

function handleInput(event: Event) {
  const target = event.target as HTMLInputElement
  if (target) emit('update:modelValue', target.value)
}
</script>

<style scoped>
.input {
  border: 1px solid var(--line-strong);
  border-radius: 12px;
  padding: 0.75rem 0.85rem;
  font: inherit;
  background: #fff;
}

.input:focus {
  outline: none;
  border-color: var(--brand-500);
  box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.18);
}
</style>
