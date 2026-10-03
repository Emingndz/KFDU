import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const { logoutMock, pushMock, toastErrorMock } = vi.hoisted(() => ({
  logoutMock: vi.fn<() => void>(),
  pushMock: vi.fn<(location: unknown) => void>(),
  toastErrorMock: vi.fn<(message: string) => void>(),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({ token: 'test-token', logout: logoutMock }),
}))

vi.mock('@/router', () => ({
  default: { currentRoute: { value: { fullPath: '/ayarlar' } }, push: pushMock },
}))

vi.mock('vue-sonner', () => ({ toast: { error: toastErrorMock } }))

import { api, apiDownload, ApiError } from './client'

type FetchResponse = { status: number; ok: boolean; json: () => Promise<unknown> }

function mockFetchOnce(response: { status: number; body?: unknown }) {
  return vi.fn<(...args: unknown[]) => Promise<FetchResponse>>().mockResolvedValue({
    status: response.status,
    ok: response.status >= 200 && response.status < 300,
    json: async () => response.body ?? null,
  })
}

describe('api client', () => {
  beforeEach(() => {
    logoutMock.mockClear()
    pushMock.mockClear()
    toastErrorMock.mockClear()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('sorgu parametrelerini kodlar, boş/undefined değerleri atlar', async () => {
    const fetchMock = mockFetchOnce({ status: 200, body: { ok: true } })
    vi.stubGlobal('fetch', fetchMock)

    await api('/search', { query: { q: 'bilim kurgu', page: 1, empty: '', skip: undefined } })

    const calledUrl = fetchMock.mock.calls[0]![0] as URL
    expect(calledUrl.searchParams.get('q')).toBe('bilim kurgu')
    expect(calledUrl.searchParams.get('page')).toBe('1')
    expect(calledUrl.searchParams.has('empty')).toBe(false)
    expect(calledUrl.searchParams.has('skip')).toBe(false)
  })

  it('token varsa Authorization başlığını ekler', async () => {
    const fetchMock = mockFetchOnce({ status: 200, body: {} })
    vi.stubGlobal('fetch', fetchMock)

    await api('/users/me')

    const options = fetchMock.mock.calls[0]![1] as RequestInit
    expect((options.headers as Record<string, string>).Authorization).toBe('Bearer test-token')
  })

  it('başarısız yanıtı detail/code/errors alanlarıyla ApiError’a çevirir', async () => {
    const fetchMock = mockFetchOnce({
      status: 422,
      body: { detail: 'Doğrulama hatası', code: 'VALIDATION_ERROR', errors: [{ field: 'email', message: 'Geçersiz' }] },
    })
    vi.stubGlobal('fetch', fetchMock)

    await expect(api('/auth/register', { method: 'POST', body: {} })).rejects.toMatchObject({
      status: 422,
      code: 'VALIDATION_ERROR',
      message: 'Doğrulama hatası',
      errors: [{ field: 'email', message: 'Geçersiz' }],
    })
  })

  it('gövdesi olmayan hatada genel mesaja düşer', async () => {
    const fetchMock = mockFetchOnce({ status: 500, body: null })
    vi.stubGlobal('fetch', fetchMock)

    await expect(api('/oops')).rejects.toThrow('Beklenmeyen bir hata oluştu')
  })

  it('204 yanıtında undefined döner', async () => {
    const fetchMock = vi.fn<(...args: unknown[]) => Promise<FetchResponse>>().mockResolvedValue({
      status: 204,
      ok: true,
      json: async () => null,
    })
    vi.stubGlobal('fetch', fetchMock)

    await expect(api('/auth/logout-all', { method: 'POST' })).resolves.toBeUndefined()
  })

  it('401 durumunda çıkış yapar, /girise yönlendirir ve tek toast gösterir', async () => {
    const fetchMock = mockFetchOnce({ status: 401, body: { detail: 'Yetkisiz', code: 'UNAUTHORIZED' } })
    vi.stubGlobal('fetch', fetchMock)

    await expect(api('/users/me')).rejects.toBeInstanceOf(ApiError)
    await expect(api('/users/me')).rejects.toBeInstanceOf(ApiError)

    expect(logoutMock).toHaveBeenCalledTimes(2)
    expect(toastErrorMock).toHaveBeenCalledTimes(1)
    expect(pushMock).toHaveBeenCalledWith({ path: '/giris', query: { redirect: '/ayarlar' } })
  })
})

describe('apiDownload', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('gövdeyi Blob, dosya adını Content-Disposition başlığından döndürür', async () => {
    const blob = new Blob(['{}'], { type: 'application/json' })
    const fetchMock = vi.fn<(...args: unknown[]) => Promise<unknown>>().mockResolvedValue({
      status: 200,
      ok: true,
      blob: async () => blob,
      json: async () => null,
      headers: new Headers({ 'Content-Disposition': 'attachment; filename="kfdu-ali-2026-10-04.json"' }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await apiDownload('/users/me/export', { query: { format: 'json' } })

    expect(result).toEqual({ blob, filename: 'kfdu-ali-2026-10-04.json' })
    const calledUrl = fetchMock.mock.calls[0]![0] as URL
    expect(calledUrl.pathname).toBe('/api/v1/users/me/export')
    expect(calledUrl.searchParams.get('format')).toBe('json')
    expect((fetchMock.mock.calls[0]![1] as RequestInit).headers).toEqual({ Authorization: 'Bearer test-token' })
  })

  it('başarısız yanıtı ApiError’a çevirir', async () => {
    vi.stubGlobal('fetch', mockFetchOnce({ status: 422, body: { detail: 'Geçersiz biçim', code: 'VALIDATION_ERROR' } }))

    await expect(apiDownload('/users/me/export')).rejects.toMatchObject({
      status: 422,
      code: 'VALIDATION_ERROR',
      message: 'Geçersiz biçim',
    })
  })
})
