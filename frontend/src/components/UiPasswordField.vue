<template>
  <div class="password-field">
    <ui-input
      v-bind="$attrs"
      :type="isVisible ? 'text' : 'password'"
      :value="modelValue"
      :disabled="disabled"
      class="password-input"
      @input="onInput"
    />

    <button
      :aria-label="isVisible ? 'Hide password' : 'Show password'"
      :aria-pressed="isVisible"
      :disabled="disabled"
      type="button"
      class="password-toggle"
      @click="isVisible = !isVisible"
    >
      <IconEye class="toggle-icon" :is-crossed="isVisible" />
    </button>
  </div>
</template>

<script setup lang="ts">
import UiInput from '@/components/UiInput.vue'
import IconEye from '@/icons/EyeIcon.vue'
import { ref } from 'vue'

interface Props {
  modelValue: string
  required?: boolean
  disabled?: boolean
}

withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()
const isVisible = ref(false)

const onInput = (event: InputEvent) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}
</script>

<style scoped>
.password-field {
  position: relative;
}

.password-input {
  width: 100%;
  padding-right: 2.8rem;
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 0.35rem;
  transform: translateY(-50%);
  width: 2.1rem;
  height: 2.1rem;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: var(--ink-600);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.password-toggle:hover {
  background: rgba(15, 23, 42, 0.06);
  color: var(--ink-800);
}

.password-toggle:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px rgba(13, 148, 136, 0.2);
}

.password-toggle:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toggle-icon {
  width: 1.05rem;
  height: 1.05rem;
}
</style>
