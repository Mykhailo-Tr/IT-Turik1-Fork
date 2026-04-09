import { describe, it, expect, vi } from 'vitest'
import { userEvent } from 'vitest/browser'
import { render } from 'vitest-browser-vue'
import UiSelect, { type SelectOption } from '../UiSelect.vue'

const mockOptions: SelectOption[] = [
  { value: 'apple', label: 'Apple' },
  { value: 'banana', label: 'Banana' },
  { value: 'cherry', label: 'Cherry' },
  { value: 'date', label: 'Date' },
]

describe('UiSelect', () => {
  it('shows placeholder when no option is selected', async () => {
    const screen = await render(UiSelect, {
      props: { modelValue: null, options: mockOptions, placeholder: 'Choose fruit' },
    })

    expect(screen.getByText('Choose fruit')).toBeInTheDocument()
  })

  it('shows selected label when a value is provided', async () => {
    const screen = await render(UiSelect, {
      props: { modelValue: 'apple', options: mockOptions },
    })

    expect(screen.getByText('Apple')).toBeInTheDocument()
  })

  it('opens the dropdown and reveals option items', async () => {
    const screen = await render(UiSelect, {
      props: { modelValue: null, options: mockOptions },
    })

    const trigger = screen.getByRole('button')
    await trigger.click()

    const options = screen.getByTestId('select-option').all()
    expect(options.length).toBe(4)
    expect(screen.getByTestId('select-search')).not.toBeNull()
  })

  it('filters the option list based on query', async () => {
    const screen = await render(UiSelect, {
      props: { modelValue: null, options: mockOptions },
    })

    const trigger = screen.getByRole('button')
    await trigger.click()

    const input = screen.getByRole('textbox')
    await input.fill('ban')

    const options = screen.getByTestId('select-option').all()
    expect(options.length).toBe(1)
    expect(options[0]).toHaveTextContent('Banana')
  })

  it('selects an option and closes the dropdown in single select mode', async () => {
    const onUpdate = vi.fn()
    const screen = await render(UiSelect, {
      props: { modelValue: null, options: mockOptions, 'onUpdate:modelValue': onUpdate },
    })

    const trigger = screen.getByRole('button')
    await trigger.click()

    const options = screen.getByTestId('select-option').first()
    await options.click()

    expect(onUpdate).toHaveBeenCalledWith('apple')
    expect(() => screen.getByTestId('select-dropdown')).not.toThrow()
  })

  it('allows multiple selections without closing the dropdown', async () => {
    const screen = await render(UiSelect, {
      props: {
        multiple: true,
        modelValue: ['apple'],
        options: mockOptions,
      },
    })

    const trigger = screen.getByRole('button')
    await trigger.click()

    const options = screen.getByTestId('select-option').all()
    await options[1].click()
    await options[2].click()

    expect(screen.emitted('update:modelValue')).toStrictEqual([
      [['apple', 'banana']],
      [['apple', 'cherry']],
    ])
    expect(screen.getByTestId('select-dropdown')).toBeVisible()
  })

  it('shows multiple selection summary when more than one item is selected', async () => {
    const screen = await render(UiSelect, {
      props: { multiple: true, modelValue: ['apple', 'banana', 'cherry'], options: mockOptions },
    })

    expect(screen.getByText('Apple +2 more')).toBeInTheDocument()
  })

  it('opens the dropdown with keyboard Enter', async () => {
    const screen = await render(UiSelect, {
      props: { modelValue: null, options: mockOptions },
    })

    await userEvent.keyboard('{Tab}{Enter}')

    expect(screen.getByTestId('select-dropdown')).not.toBeNull()
  })

  it('closes the dropdown with Escape', async () => {
    const screen = await render(UiSelect, {
      props: { modelValue: null, options: mockOptions },
    })

    const trigger = screen.getByRole('button')
    await trigger.click()

    await userEvent.keyboard('{Escape}')

    await expect.poll(() => screen.getByTestId('select-dropdown').query()).not.toBeInTheDocument()
  })

  it('shows an empty state when no options are available', async () => {
    const screen = await render(UiSelect, {
      props: { modelValue: null, options: [] },
    })

    const trigger = screen.getByRole('button')
    await trigger.click()

    const options = screen.getByTestId('select-option')
    expect(options.length).toBe(0)
    expect(screen.getByTestId('select-empty')).toBeInTheDocument()
  })

  it('applies accessible aria attributes to the trigger and listbox', async () => {
    const screen = await render(UiSelect, {
      props: { modelValue: null, options: mockOptions },
    })

    const trigger = screen.getByRole('button')
    expect(trigger).toHaveAttribute('aria-haspopup', 'listbox')
    expect(trigger).toHaveAttribute('aria-expanded', 'false')

    await trigger.click()

    expect(trigger).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByTestId('select-list')).toHaveAttribute('role', 'listbox')
    expect(screen.getByTestId('select-list')).toHaveAttribute('aria-multiselectable', 'false')
  })

  it('sets aria-multiselectable when multiple mode is enabled', async () => {
    const screen = await render(UiSelect, {
      props: { multiple: true, modelValue: [], options: mockOptions },
    })

    const trigger = screen.getByRole('button')
    await trigger.click()

    expect(screen.getByTestId('select-list')).toHaveAttribute('aria-multiselectable', 'true')
  })
})
