<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="modal-backdrop" @click.self="handleBackdropClick">
        <div
          class="modal-card"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="props.title"
          :style="{ width: `min(100%, ${maxWidth})` }"
        >
          <!-- Header -->
          <div v-if="$slots.title || title" class="modal-header">
            <slot name="title">
              <h3 :id="props.title" class="modal-title">{{ title }}</h3>
            </slot>
            <ui-button variant="outline" size="sm" @click="close" aria-label="Close">
              <CrossIcon />
            </ui-button>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <slot />
          </div>

          <!-- Footer -->
          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import CrossIcon from '@/icons/CrossIcon.vue'
import UiButton from './UiButton.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: '',
  },
  maxWidth: {
    type: String,
    default: '520px',
  },
})

const emit = defineEmits(['update:modelValue', 'close'])

function close() {
  emit('update:modelValue', false)
  emit('close')
}

function handleBackdropClick() {
  close()
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(3px);
  display: grid;
  place-items: center;
  z-index: 50;
  padding: 1rem;
}

.modal-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid var(--line-soft, #e2e8f0);
  box-shadow: var(
    --shadow-lg,
    0 4px 6px -1px rgba(0, 0, 0, 0.07),
    0 20px 40px -8px rgba(15, 23, 42, 0.18)
  );
  overflow: hidden;
}

/* ---- header ---- */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem 0;
}

.modal-title {
  margin: 0;
  font-family: var(--font-display, inherit);
  font-size: 1.05rem;
  font-weight: 650;
  color: #0f172a;
  letter-spacing: -0.01em;
}

.modal-close {
  flex-shrink: 0;
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 7px;
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  transition:
    background 0.15s,
    color 0.15s;
}

.modal-close:hover {
  background: #f1f5f9;
  color: #475569;
}

/* ---- body ---- */
.modal-body {
  padding: 1rem 1.5rem;
}

/* ---- footer ---- */
.modal-footer {
  padding: 0 1.5rem 1.25rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
}

/* ---- transitions ---- */
.modal-enter-active {
  transition: opacity 0.2s ease;
}
.modal-leave-active {
  transition: opacity 0.18s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .modal-card {
  transform: scale(0.98);
}
.modal-leave-to .modal-card {
  transform: scale(0.99);
}
</style>
