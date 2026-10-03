import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const mocks = vi.hoisted(() => ({ fetchMe: vi.fn<() => Promise<unknown>>() }))

vi.mock('@/api/client', () => ({
  ApiError: class ApiError extends Error {
    constructor(
      public status: number,
      public code: string,
      message: string,
    ) {
      super(message)
    }
  },
}))
vi.mock('@/api/users', () => ({ fetchMeRequest: mocks.fetchMe }))
vi.mock('@/api/auth', () => ({ loginRequest: vi.fn<() => void>(), registerRequest: vi.fn<() => void>() }))

import { ApiError } from '@/api/client'
import { useAuthStore } from './auth'

describe('auth store — fetchMe', () => {
  beforeEach(() => {
    localStorage.clear()
    localStorage.setItem('kfdu_token', 'eski-token')
    setActivePinia(createPinia())
    mocks.fetchMe.mockReset()
  })

  it('ağ yokken (çevrimdışı PWA) token korunur, oturum düşmez', async () => {
    mocks.fetchMe.mockRejectedValue(new TypeError('Failed to fetch'))
    const auth = useAuthStore()

    await expect(auth.fetchMe()).rejects.toThrow('Failed to fetch')
    expect(auth.token).toBe('eski-token')
    expect(auth.isAuthenticated).toBe(true)
    expect(localStorage.getItem('kfdu_token')).toBe('eski-token')
  })

  it('sunucu geçici hata verirse (5xx) token korunur', async () => {
    mocks.fetchMe.mockRejectedValue(new ApiError(503, 'SERVICE_UNAVAILABLE', 'Bakımda'))
    const auth = useAuthStore()

    await expect(auth.fetchMe()).rejects.toBeInstanceOf(ApiError)
    expect(auth.isAuthenticated).toBe(true)
  })

  it('oturum geçersizse (401) token silinir', async () => {
    mocks.fetchMe.mockRejectedValue(new ApiError(401, 'UNAUTHORIZED', 'Oturum geçersiz'))
    const auth = useAuthStore()

    await expect(auth.fetchMe()).rejects.toBeInstanceOf(ApiError)
    expect(auth.token).toBeNull()
    expect(localStorage.getItem('kfdu_token')).toBeNull()
  })
})
