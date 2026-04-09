import { describe, it, expect } from 'vitest'
import { render } from 'vitest-browser-vue'
import UiCard from '../UiCard.vue'

describe('UiCard', () => {
  it('renders default slot content', async () => {
    const screen = render(UiCard, {
      slots: { default: 'Card content' },
    })

    expect(screen.getByText('Card content')).toBeInTheDocument()
  })

  it('renders a header only when the header slot is provided', async () => {
    const withHeader = render(UiCard, {
      slots: { header: 'Header text' },
    })

    expect(withHeader.locator.getByText('Header text')).toBeInTheDocument()

    const withoutHeader = render(UiCard, {
      slots: { default: 'Body content' },
    })

    expect(withoutHeader.locator.getByText('Header text')).not.toBeInTheDocument()
  })

  it('renders a footer only when the footer slot is provided', async () => {
    const withFooter = render(UiCard, {
      slots: { footer: 'Footer text' },
    })

    expect(withFooter.locator.getByText('Footer text')).toBeInTheDocument()

    const withoutFooter = render(UiCard, {
      slots: { default: 'Body content' },
    })

    expect(withoutFooter.locator.getByText('Footer text')).not.toBeInTheDocument()
  })

  it('renders all slots together', async () => {
    const screen = render(UiCard, {
      slots: {
        header: 'Header',
        default: 'Body',
        footer: 'Footer',
      },
    })

    const card = screen.getByRole('article')

    expect(card.getByText('Header')).toBeInTheDocument()
    expect(card.getByText('Body')).toBeInTheDocument()
    expect(card.getByText('Footer')).toBeInTheDocument()
  })
})
