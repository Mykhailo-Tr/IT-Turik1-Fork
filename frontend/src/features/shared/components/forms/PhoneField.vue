<template>
  <div class="phone-field">
    <VueTelInput
      v-model="phoneUiValue"
      mode="international"
      :auto-default-country="true"
      :dropdown-options="{ showDialCodeInSelection: true, showSearchBox: true, showFlags: true }"
      :input-options="{ showDialCode: true, placeholder }"
      :valid-characters-only="true"
      class="phone-input"
    />
    <small v-if="error" class="text-error">{{ error }}</small>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { VueTelInput } from 'vue-tel-input'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  error: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: 'Enter phone number',
  },
})

const emit = defineEmits(['update:modelValue'])
const phoneUiValue = ref(props.modelValue || '')

const normalizePhoneNumber = (value) => {
  if (!value) {
    return ''
  }

  const hasPlus = value.trim().startsWith('+')
  const digitsOnly = value.replace(/[^\d]/g, '')
  if (!digitsOnly) {
    return ''
  }

  return hasPlus ? `+${digitsOnly}` : digitsOnly
}

watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue !== phoneUiValue.value) {
      phoneUiValue.value = newValue || ''
    }
  },
)

watch(phoneUiValue, (newValue) => {
  emit('update:modelValue', normalizePhoneNumber(newValue))
})
</script>

<style scoped>
.phone-field {
  display: grid;
  gap: 0.35rem;
}

.phone-input {
  width: 100%;
}

:deep(.vti) {
  border-radius: 12px;
  border: 1px solid var(--line-strong);
  background: #fff;
  box-shadow: none;
}

:deep(.vti__input) {
  font: inherit;
  padding: 0.75rem 0.85rem;
}

:deep(.vti:focus-within) {
  border-color: var(--brand-500);
  box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.18);
}
</style>

