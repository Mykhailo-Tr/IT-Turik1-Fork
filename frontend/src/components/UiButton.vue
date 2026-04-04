<template>
  <component
    :is="props.asLink ? RouterLink : 'button'"
    :to="props.asLink ? props.to : undefined"
    type="button"
    :class="['btn', variantClass, sizeClass]"
    v-bind="$attrs"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const variants = {
  default: 'default-btn',
  outline: 'outline-btn',
  'outline-accent': 'outline-accent-btn',
  ghost: 'ghost-btn',
  danger: 'danger-btn',
  warning: 'warning-btn',
} as const

const sizes = {
  xs: 'btn-xs',
  sm: 'btn-sm',
  md: 'btn-md',
  lg: 'btn-lg',
} as const

type Size = keyof typeof sizes

type Variant = keyof typeof variants

type Props = {
  asLink?: boolean
  to?: string
  variant?: Variant
  size?: Size
}

const props = withDefaults(defineProps<Props>(), {
  asLink: false,
  variant: 'default',
  size: 'md',
})

const variantClass = computed(() => variants[props.variant])
const sizeClass = computed(() => sizes[props.size])
</script>

<style scoped>
.btn-sm {
  padding: 0.45rem 0.7rem;
  font-size: 0.85rem !important;
}

.btn-md {
  padding: 0.7rem 1rem;
  font-size: 1rem !important;
}

.btn-lg {
  padding: 0.9rem 1.35rem;
  font-size: 1.1rem !important;
}

.btn {
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font: inherit;
  font-weight: 700;
  border-radius: var(--radius);
  background: rgba(255, 255, 255, 0.12);
  color: black;
  cursor: pointer;
  outline: none;
  text-decoration: none;
  transition:
    background 0.2s ease,
    color 0.2s ease,
    border-color 0.2s ease,
    opacity 0.2s ease,
    box-shadow 0.2s ease;
}

.btn:focus {
  box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.18);
}

.btn:hover {
  background: rgba(185, 185, 185, 0.15);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.default-btn {
  border: none;
  color: white;
  background: linear-gradient(120deg, var(--brand-600), var(--brand-500));
}

.default-btn:hover {
  border: none;
  background: linear-gradient(120deg, var(--brand-600), var(--brand-500));
  opacity: 0.75;
}

.outline-btn,
.outline-accent-btn {
  border: 1px solid var(--line-strong);
}

.outline-accent-btn:active,
.outline-accent-btn:hover {
  color: var(--brand-700);
  background: rgba(20, 184, 165, 0.058);
}

.danger-btn {
  border: 1px solid #dc2626;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 12px;
}

.danger-btn:focus {
  box-shadow: 0 0 0 3px rgb(148 13 13 / 18%);
}

.danger-btn:hover {
  background: #f5cdcd;
}

.warning-btn {
  border: 1px solid #d97706;
  background: #fef3c7;
  color: #92400e;
}

.warning-btn:focus {
  box-shadow: 0 0 0 3px rgb(148 118 13 / 18%);
}

.warning-btn:hover {
  background: #ffea96;
}
</style>
