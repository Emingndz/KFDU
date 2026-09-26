import { describe, it, expect } from 'vitest'
import { useConfirm } from '@/composables/useConfirm'

describe('useConfirm', () => {
  it('resolves true and closes the dialog when confirmed', async () => {
    const { confirm, resolve, state } = useConfirm()
    const promise = confirm({ title: 'Emin misin?', message: 'Devam?' })
    expect(state.open).toBe(true)
    expect(state.title).toBe('Emin misin?')
    resolve(true)
    await expect(promise).resolves.toBe(true)
    expect(state.open).toBe(false)
  })

  it('resolves false when cancelled', async () => {
    const { confirm, resolve } = useConfirm()
    const promise = confirm({ title: 'Sil', message: 'Emin misin?' })
    resolve(false)
    await expect(promise).resolves.toBe(false)
  })

  it('uses default confirm/cancel texts when not provided', () => {
    const { confirm, state, resolve } = useConfirm()
    void confirm({ title: 'X', message: 'Y' })
    expect(state.confirmText).toBe('Onayla')
    expect(state.cancelText).toBe('Vazgeç')
    resolve(false)
  })

  it('applies custom confirm text and danger flag', () => {
    const { confirm, state, resolve } = useConfirm()
    void confirm({ title: 'Sil', message: 'Emin misin?', confirmText: 'Evet, sil', danger: true })
    expect(state.confirmText).toBe('Evet, sil')
    expect(state.danger).toBe(true)
    resolve(false)
  })
})
