import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { defineComponent, h, ref } from 'vue'
import ErrorBoundary from '@/components/layout/ErrorBoundary.vue'

const Boom = defineComponent({
  setup() {
    throw new Error('kaboom')
  },
  render: () => null,
})

async function mountWithRouter(slotContent: () => ReturnType<typeof h> | string) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/baska', component: { template: '<div />' } },
    ],
  })
  await router.push('/')
  await router.isReady()

  const wrapper = mount(ErrorBoundary, {
    global: { plugins: [router] },
    slots: { default: slotContent },
  })
  return { wrapper, router }
}

describe('ErrorBoundary', () => {
  it('hata yokken slot içeriğini normal şekilde gösterir', async () => {
    const { wrapper } = await mountWithRouter(() => h('p', 'merhaba'))
    expect(wrapper.text()).toContain('merhaba')
    expect(wrapper.text()).not.toContain('Sayfayı yenile')
  })

  it('bir alt bileşen hata fırlattığında yedek arayüzü gösterir', async () => {
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const { wrapper } = await mountWithRouter(() => h(Boom))
    expect(wrapper.text()).toContain('Sayfayı yenile')
    errorSpy.mockRestore()
  })

  it('rota değiştiğinde hata durumunu sıfırlar', async () => {
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const shouldThrow = ref(true)
    const ConditionalBoom = defineComponent({
      setup() {
        if (shouldThrow.value) throw new Error('kaboom')
        return () => h('p', 'düzeldi')
      },
    })

    const { wrapper, router } = await mountWithRouter(() => h(ConditionalBoom))
    expect(wrapper.text()).toContain('Sayfayı yenile')

    shouldThrow.value = false
    await router.push('/baska')
    expect(wrapper.text()).toContain('düzeldi')
    errorSpy.mockRestore()
  })
})
