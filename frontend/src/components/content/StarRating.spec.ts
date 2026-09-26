import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import StarRating from './StarRating.vue'

describe('StarRating', () => {
  it('tıklanan yarıma göre doğru 1-10 değerini yayar', async () => {
    const wrapper = mount(StarRating, { props: { modelValue: null } })
    const halfButtons = wrapper.findAll('button')
    await halfButtons[0]!.trigger('click')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([1])
  })

  it('yarım yıldızlar 1-10 aralığına doğru eşlenir (sağ yarım = çift değer)', async () => {
    const wrapper = mount(StarRating, { props: { modelValue: null } })
    const halfButtons = wrapper.findAll('button')
    await halfButtons[3]!.trigger('click')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([4])
  })

  it('aynı değere tekrar tıklayınca temizler', async () => {
    const wrapper = mount(StarRating, { props: { modelValue: 4 } })
    const halfButtons = wrapper.findAll('button')
    await halfButtons[3]!.trigger('click')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([null])
  })

  it('ok tuşlarıyla değeri 1 artırıp azaltır', async () => {
    const wrapper = mount(StarRating, { props: { modelValue: 5 } })
    const slider = wrapper.find('[role="slider"]')
    await slider.trigger('keydown', { key: 'ArrowRight' })
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([6])
    await slider.trigger('keydown', { key: 'ArrowLeft' })
    expect(wrapper.emitted('update:modelValue')?.[1]).toEqual([4])
  })

  it('Home/End sınırlara gider, Delete temizler', async () => {
    const wrapper = mount(StarRating, { props: { modelValue: 5 } })
    const slider = wrapper.find('[role="slider"]')
    await slider.trigger('keydown', { key: 'Home' })
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([1])
    await slider.trigger('keydown', { key: 'End' })
    expect(wrapper.emitted('update:modelValue')?.[1]).toEqual([10])
    await slider.trigger('keydown', { key: 'Delete' })
    expect(wrapper.emitted('update:modelValue')?.[2]).toEqual([null])
  })

  it('değer 10u aşamaz veya 1in altına inemez', async () => {
    const wrapper = mount(StarRating, { props: { modelValue: 10 } })
    const slider = wrapper.find('[role="slider"]')
    await slider.trigger('keydown', { key: 'ArrowRight' })
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([10])
  })

  it('salt okunur modda tıklanabilir yarım/klavye alanı oluşturmaz', () => {
    const wrapper = mount(StarRating, { props: { modelValue: 5, readonly: true } })
    expect(wrapper.findAll('button').length).toBe(0)
    expect(wrapper.find('[role="slider"]').exists()).toBe(false)
  })

  it('değeri tam/yarım/boş yıldız dolgusuyla doğru render eder', () => {
    const wrapper = mount(StarRating, { props: { modelValue: 7, readonly: true } })
    const fillSpans = wrapper.findAll('span.absolute.inset-0.overflow-hidden')
    expect(fillSpans[0]!.attributes('style')).toContain('100%')
    expect(fillSpans[2]!.attributes('style')).toContain('100%')
    expect(fillSpans[3]!.attributes('style')).toContain('50%')
    expect(fillSpans[4]!.attributes('style')).toContain('0%')
  })
})
