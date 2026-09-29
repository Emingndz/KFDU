import { afterEach, describe, expect, it } from 'vitest'
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { defineComponent } from 'vue'
import { useKeyboardShortcuts } from '@/composables/useKeyboardShortcuts'

let activeWrapper: VueWrapper | null = null

afterEach(() => {
  activeWrapper?.unmount()
  activeWrapper = null
})

async function setup() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div>akış</div>' } },
      { path: '/kesfet', component: { template: '<div>keşfet</div>' } },
      { path: '/baslangic', component: { template: '<div>başlangıç</div>' } },
    ],
  })
  await router.push('/baslangic')
  await router.isReady()

  let helpOpenRef: { value: boolean } | undefined
  const Host = defineComponent({
    setup() {
      const { helpOpen } = useKeyboardShortcuts()
      helpOpenRef = helpOpen
      return () => null
    },
  })
  activeWrapper = mount(Host, { global: { plugins: [router] } })

  return { router, helpOpen: () => helpOpenRef! }
}

function press(key: string, target?: EventTarget) {
  const event = new KeyboardEvent('keydown', { key, bubbles: true, cancelable: true })
  if (target) Object.defineProperty(event, 'target', { value: target })
  window.dispatchEvent(event)
}

describe('useKeyboardShortcuts', () => {
  it('"?" tuşu kısayol yardımını açar', async () => {
    const { helpOpen } = await setup()
    expect(helpOpen().value).toBe(false)
    press('?')
    expect(helpOpen().value).toBe(true)
  })

  it('"g" sonra "f" akışa gider', async () => {
    const { router } = await setup()
    press('g')
    press('f')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/')
  })

  it('"g" sonra "k" keşfete gider', async () => {
    const { router } = await setup()
    press('g')
    press('k')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/kesfet')
  })

  it('bir metin girdisine yazarken kısayolları tetiklemez', async () => {
    const { helpOpen } = await setup()
    const input = document.createElement('input')
    document.body.appendChild(input)
    press('?', input)
    expect(helpOpen().value).toBe(false)
    input.remove()
  })
})
