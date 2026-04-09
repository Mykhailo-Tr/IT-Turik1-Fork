import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiBadge from '../UiBadge.vue'

describe('UiBadge', () => {
  it('renders slot content correctly', () => {
    const wrapper = render(UiBadge, {
      slots: { default: 'Badge text' },
    })

    expect(wrapper.getByText('Badge text')).toBeInTheDocument()
  })

  it('supports the variant prop without breaking rendering', () => {
    const wrapper = render(UiBadge, {
      props: { variant: 'red' },
      slots: { default: 'Badge text' },
    })

    expect(wrapper.getByText('Badge text')).toBeInTheDocument
  })
})
