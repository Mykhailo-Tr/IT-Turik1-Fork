<template>
  <input
    :class="['input', { invalid: isInvalid }]"
    type="text"
    :value="modelValue"
    @input="handleInput"
  />
</template>

<script setup lang="ts">
interface Props {
  modelValue?: string | number
  isInvalid?: boolean
}

withDefaults(defineProps<Props>(), {
  modelValue: '',
  invalid: false,
})
const emit = defineEmits(['update:modelValue'])

function handleInput(event: Event) {
  const target = event.target as HTMLInputElement
  if (target) emit('update:modelValue', target.value)
}
</script>

<style scoped>
.input {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0.75rem 0.85rem;
  font: inherit;
  background: var(--input);
  color: var(--foreground);
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.input:focus {
  outline: none;
  box-shadow: 0 0 0 3px var(--ring);
}

.input:disabled {
  cursor: not-allowed;
}

.invalid {
  border-color: var(--destructive);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--destructive) 12%, transparent);
}

.input[type='radio']:focus {
  box-shadow: none;
}
</style>
