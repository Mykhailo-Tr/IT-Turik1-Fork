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
  modelValue?: string
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
  border: 1px solid var(--line-strong);
  border-radius: 12px;
  padding: 0.75rem 0.85rem;
  font: inherit;
  background: #fff;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.input:disabled {
  cursor: not-allowed;
}

.invalid {
  border-color: rgba(220, 38, 38, 0.7);
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.12);
}

.input[type='radio']:focus {
  box-shadow: none;
}

.input:focus {
  outline: none;
  border-color: var(--brand-500);
  box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.18);
}
</style>
