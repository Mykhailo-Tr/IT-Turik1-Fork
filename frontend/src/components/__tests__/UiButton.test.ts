import { describe, it, expect } from 'vitest'
import UiButton from '../UiButton.vue'
import { createRouter, createMemoryHistory } from 'vue-router'
import { render } from 'vitest-browser-vue'

const createTestRouter = () =>
  createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/', component: { template: '<div />' } }],
  })

describe('UiButton', () => {
  it('renders as a native button by default', () => {
    const { locator } = render(UiButton, {
      slots: { default: 'Submit' },
    })

    const button = locator.getByRole('button')
    expect(button).toBeInTheDocument()
    expect(button).toHaveTextContent('Submit')
    expect(button).toHaveAttribute('type', 'button')
  })

  it('forwards disabled attribute to the native button', () => {
    const { locator, debug } = render(UiButton, {
      attrs: { disabled: true },
      slots: { default: 'Disabled' },
    })

    const button = locator.getByRole('button')
    debug(button)
    expect(button).toBeDisabled()
  })

  it('renders as a link when asLink is true', async () => {
    const router = createTestRouter()

    const { locator } = render(UiButton, {
      props: { asLink: true, to: '/target' },
      global: {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        plugins: [router as any],
      },
      slots: { default: 'Navigate' },
    })

    const link = locator.getByRole('link')
    expect(link).toBeInTheDocument()
    expect(link).toHaveTextContent('Navigate')
    expect(link).toHaveAttribute('href', '/target')

    await link.click()
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/target')
  })
})
