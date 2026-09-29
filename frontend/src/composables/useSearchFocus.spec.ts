import { describe, expect, it } from 'vitest'
import { consumeSearchFocusRequest, requestSearchFocus } from '@/composables/useSearchFocus'

describe('useSearchFocus', () => {
  it('bekleyen bir istek olmadığında false döner', () => {
    expect(consumeSearchFocusRequest()).toBe(false)
  })

  it('istek işaretlenince bir kez true döner, sonra sıfırlanır', () => {
    requestSearchFocus()
    expect(consumeSearchFocusRequest()).toBe(true)
    expect(consumeSearchFocusRequest()).toBe(false)
  })
})
