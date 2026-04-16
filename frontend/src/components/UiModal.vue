<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="modal-backdrop"
        data-testid="modal-backdrop"
        @click.self="handleBackdropClick"
      >
        <ui-card
          class="modal-card"
          role="dialog"
          aria-modal="true"
          :style="{ width: `min(100%, ${maxWidth})` }"
        >
          <template #header>
            <div class="modal-header">
              <slot v-if="$slots.title" class="modal-title" name="title" />

              <ui-button
                style="margin-left: auto"
                variant="secondary"
                size="sm"
                @click="close"
                aria-label="Close"
              >
                <CrossIcon />
              </ui-button>
            </div>
          </template>

          <div>
            <slot />
          </div>

          <template #footer>
            <div v-if="$slots.footer" class="modal-footer">
              <slot name="footer" />
            </div>
          </template>
        </ui-card>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import CrossIcon from '@/icons/CrossIcon.vue'
import UiButton from './UiButton.vue'
import { onMounted, onUnmounted } from 'vue'
import UiCard from './UiCard.vue'

interface Props {
  modelValue: boolean
  maxWidth?: string
}

const props = withDefaults(defineProps<Props>(), {
  maxWidth: '520px',
})

const emit = defineEmits(['update:modelValue', 'close'])

function close() {
  emit('update:modelValue', false)
  emit('close')
}

function handleBackdropClick() {
  close()
}

function handleEscapeKey(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.modelValue) {
    close()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleEscapeKey)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleEscapeKey)
})
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
  background: var(--card);
  color: var(--card-foreground);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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
  color: color-mix(in srgb, var(--foreground) 45%, transparent);
  cursor: pointer;
  transition:
    background 0.15s,
    color 0.15s;
}

.modal-close:hover {
  background: color-mix(in srgb, var(--foreground) 8%, transparent);
  color: color-mix(in srgb, var(--foreground) 72%, transparent);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
}

.modal-enter-active,
.modal-leave-active {
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: translateY(4px);
}
</style>
