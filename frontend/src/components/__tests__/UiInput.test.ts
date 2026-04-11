import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiInput from '../UiInput.vue'

describe('UiInput', () => {
  it('renders the provided modelValue', async () => {
    const screen = await render(UiInput, {
      props: { modelValue: 'Hello' },
    })

    const input = screen.getByRole('textbox')
    expect(input).toBeVisible()
    expect(input).toHaveValue('Hello')
  })

  it('updates value when the user types', async () => {
    const screen = await render(UiInput, {
      props: { modelValue: '' },
    })

    const input = screen.getByRole('textbox')
    await input.fill('New value')

    expect(input).toHaveValue('New value')
  })

  it('applies invalid prop correctly', async () => {
    const screen = await render(UiInput, {
      props: { modelValue: '', isInvalid: true },
      attrs: { placeholder: 'Type here', disabled: true },
    })

    const input = screen.getByRole('textbox')
    expect(input).toHaveClass('invalid')
  })

  it('forwards native input attributes', async () => {
    const screen = await render(UiInput, {
      props: { modelValue: '' },
      attrs: { placeholder: 'Type here', disabled: true },
    })

    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('placeholder', 'Type here')
    expect(input).toBeDisabled()
  })
})
