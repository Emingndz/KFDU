import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseAvatar from '@/components/ui/BaseAvatar.vue'

describe('BaseAvatar', () => {
  it('shows initials from the first and last name when there is no image', () => {
    const wrapper = mount(BaseAvatar, { props: { name: 'Ada Lovelace' } })
    expect(wrapper.text()).toBe('AL')
  })

  it('uses the first two letters for a single-word name', () => {
    const wrapper = mount(BaseAvatar, { props: { name: 'Zeynep' } })
    expect(wrapper.text()).toBe('ZE')
  })

  it('produces the same background color for the same name', () => {
    const a = mount(BaseAvatar, { props: { name: 'Kerem Yılmaz' } })
    const b = mount(BaseAvatar, { props: { name: 'Kerem Yılmaz' } })
    expect(a.attributes('style')).toBe(b.attributes('style'))
  })

  it('produces a different background color for a different name', () => {
    const a = mount(BaseAvatar, { props: { name: 'Kerem Yılmaz' } })
    const b = mount(BaseAvatar, { props: { name: 'Ada Lovelace' } })
    expect(a.attributes('style')).not.toBe(b.attributes('style'))
  })

  it('falls back to initials when the image fails to load', async () => {
    const wrapper = mount(BaseAvatar, { props: { name: 'Ada Lovelace', src: '/broken.jpg' } })
    expect(wrapper.find('img').exists()).toBe(true)
    await wrapper.find('img').trigger('error')
    expect(wrapper.find('img').exists()).toBe(false)
    expect(wrapper.text()).toBe('AL')
  })
})
