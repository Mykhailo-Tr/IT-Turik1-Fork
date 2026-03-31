<template>
  <div class="select-wrapper" :class="{ open: isOpen }" ref="wrapperRef">
    <ui-button
      variant="outline-accent"
      class="select-trigger"
      @click="toggleOpen"
      @keydown="handleTriggerKeydown"
      :aria-expanded="isOpen"
      aria-haspopup="listbox"
    >
      <span class="select-value">{{ selectedLabel }}</span>
      <arrow-down class="select-chevron" />
    </ui-button>

    <Transition name="dropdown">
      <ul
        v-if="isOpen"
        class="select-dropdown"
        role="listbox"
        :aria-activedescendant="activeDescendant"
        ref="listRef"
        @keydown="handleListKeydown"
        tabindex="-1"
      >
        <li
          v-for="(option, index) in options"
          :key="option.value"
          :id="`option-${option.value}`"
          class="select-option"
          :class="{
            selected: option.value === modelValue,
            focused: index === focusedIndex,
          }"
          role="option"
          :aria-selected="option.value === modelValue"
          @click="selectOption(option)"
          @mouseenter="focusedIndex = index"
        >
          {{ option.label }}
          <selected-icon v-if="option.value === modelValue" class="select-check" />
        </li>
      </ul>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import UiButton from './UiButton.vue'
import ArrowDown from '@/icons/ArrowDown.vue'
import SelectedIcon from '@/icons/SelectedIcon.vue'

export type SelectOptionValue = string | number

export interface SelectOption {
  value: SelectOptionValue
  label: string
}

interface Props {
  modelValue?: SelectOptionValue | null
  options?: SelectOption[]
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  options: () => [],
  placeholder: 'Select an option',
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: SelectOptionValue): void
}>()

const isOpen = ref<boolean>(false)
const focusedIndex = ref<number>(-1)
const wrapperRef = ref<HTMLDivElement | null>(null)
const listRef = ref<HTMLUListElement | null>(null)

const selectedLabel = computed<string>(() => {
  const found = props.options.find((o) => o.value === props.modelValue)
  return found ? found.label : props.placeholder
})

const activeDescendant = computed<string | undefined>(() => {
  if (focusedIndex.value < 0) return undefined
  const opt = props.options[focusedIndex.value]
  return opt ? `option-${opt.value}` : undefined
})

watch(isOpen, async (opened) => {
  if (opened) {
    const selectedIdx = props.options.findIndex((o) => o.value === props.modelValue)
    focusedIndex.value = selectedIdx >= 0 ? selectedIdx : 0
    await nextTick()
    listRef.value?.focus()
    scrollToFocused()
  } else {
    focusedIndex.value = -1
  }
})

function toggleOpen() {
  isOpen.value = !isOpen.value
}

async function selectOption(option: SelectOption) {
  emit('update:modelValue', option.value)
  wrapperRef.value?.querySelector<HTMLElement>('.select-trigger')?.focus()
}

function handleTriggerKeydown(e: KeyboardEvent) {
  switch (e.key) {
    case 'Enter':
    case 'ArrowDown':
    case 'ArrowUp':
      e.preventDefault()
      isOpen.value = true
      break
    case 'Escape':
      isOpen.value = false
      break
  }
}

function handleListKeydown(e: KeyboardEvent) {
  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault()
      focusedIndex.value = Math.min(focusedIndex.value + 1, props.options.length - 1)
      scrollToFocused()
      break
    case 'ArrowUp':
      e.preventDefault()
      focusedIndex.value = Math.max(focusedIndex.value - 1, 0)
      scrollToFocused()
      break
    case 'Home':
      e.preventDefault()
      focusedIndex.value = 0
      scrollToFocused()
      break
    case 'End':
      e.preventDefault()
      focusedIndex.value = props.options.length - 1
      scrollToFocused()
      break
    case 'Enter':
      e.preventDefault()
      if (focusedIndex.value >= 0) {
        selectOption(props.options[focusedIndex.value]!)
      }
      isOpen.value = false
      break
    case 'Escape':
    case 'Tab':
      e.preventDefault()
      isOpen.value = false
      wrapperRef.value?.querySelector<HTMLElement>('.select-trigger')?.focus()
      break
  }
}

function scrollToFocused() {
  nextTick(() => {
    const list = listRef.value
    if (!list) return
    const focused = list.children[focusedIndex.value] as HTMLElement | undefined
    if (!focused) return

    const listPadding = parseFloat(getComputedStyle(list).paddingBottom)
    const itemBottom = focused.offsetTop + focused.offsetHeight
    const visibleBottom = list.scrollTop + list.clientHeight

    if (itemBottom + listPadding > visibleBottom) {
      list.scrollTop = itemBottom + listPadding - list.clientHeight
    }

    const listPaddingTop = parseFloat(getComputedStyle(list).paddingTop)
    if (focused.offsetTop - listPaddingTop < list.scrollTop) {
      list.scrollTop = focused.offsetTop - listPaddingTop
    }
  })
}

function handleOutsideClick(e: MouseEvent) {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', handleOutsideClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', handleOutsideClick))
</script>

<style scoped>
.select-wrapper {
  position: relative;
  display: inline-block;
  min-width: 200px;
}

.main-btn {
  border: 1px solid var(--line-strong);
  border-radius: 12px;
  padding: 0.75rem 0.85rem;
  font: inherit;
  background: #fff;
}

.select-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  cursor: pointer;
  color: inherit;
  text-align: left;
}

.select-chevron {
  flex-shrink: 0;
  color: #9ca3af;
  transition: transform 0.2s ease;
}

.select-wrapper.open .select-chevron {
  transform: rotate(180deg);
}

.select-value {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.select-dropdown {
  position: absolute;
  top: calc(100% + 3px);
  left: 0;
  right: 0;
  z-index: 50;
  list-style: none;
  margin: 0;
  padding: 0.35rem;
  background: #fff;
  border: 1px solid var(--line-strong);
  border-radius: 12px;
  box-shadow: 0 8px 20px rgb(0 0 0 / 11%);
  overflow: hidden;
  outline: none;
  max-height: 260px;
  overflow-y: auto;
}

.select-dropdown:focus-visible {
  border-color: var(--brand-500);
  box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.18);
}

.select-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
  color: inherit;
  transition: background 0.1s ease;
}

.select-option:hover,
.select-option.focused {
  background: #f3f4f6;
}

.select-option.selected {
  background: #f0fdf4;
  color: #15803d;
  font-weight: 500;
}

.select-option.selected.focused {
  background: #dcfce7;
}

.select-check {
  flex-shrink: 0;
  color: #16a34a;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
}
</style>
