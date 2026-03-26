<template>
  <div class="password-field">
    <input
      :id="id"
      :name="name"
      :value="modelValue"
      :type="isVisible ? 'text' : 'password'"
      :autocomplete="autocomplete"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      class="input-control password-input"
      @input="onInput"
    />

    <button
      type="button"
      class="password-toggle"
      :aria-label="isVisible ? 'Hide password' : 'Show password'"
      :aria-pressed="isVisible"
      :disabled="disabled"
      @click="isVisible = !isVisible"
    >
      <svg
        v-if="isVisible"
        class="toggle-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-5 0-9.27-3.11-11-8 1.07-2.99 3.16-5.42 5.74-6.88" />
        <path d="M1 1l22 22" />
        <path d="M9.9 4.24A10.5 10.5 0 0 1 12 4c5 0 9.27 3.11 11 8a11.54 11.54 0 0 1-4.17 5.94" />
        <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24" />
      </svg>
      <svg
        v-else
        class="toggle-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
        <circle cx="12" cy="12" r="3" />
      </svg>
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  id: {
    type: String,
    default: '',
  },
  name: {
    type: String,
    default: '',
  },
  autocomplete: {
    type: String,
    default: 'current-password',
  },
  placeholder: {
    type: String,
    default: '',
  },
  required: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])
const isVisible = ref(false)

const onInput = (event) => {
  emit('update:modelValue', event.target.value)
}
</script>

<style scoped>
.password-field {
  position: relative;
}

.password-input {
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
