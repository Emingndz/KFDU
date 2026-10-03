import { toast } from 'vue-sonner'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'
import { filenameFromDisposition } from '@/utils/download'

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public errors: { field: string; message: string }[] = [],
  ) {
    super(message)
  }
}

const BASE = import.meta.env.VITE_API_URL ?? '/api/v1'

let unauthorizedToastTimer: ReturnType<typeof setTimeout> | null = null

function handleUnauthorized() {
  useAuthStore().logout()
  const redirect = router.currentRoute.value.fullPath
  router.push({ path: '/giris', query: { redirect } })

  if (!unauthorizedToastTimer) {
    toast.error('Oturumun sona erdi, lütfen tekrar giriş yap')
  }
  if (unauthorizedToastTimer) clearTimeout(unauthorizedToastTimer)
  unauthorizedToastTimer = setTimeout(() => {
    unauthorizedToastTimer = null
  }, 1000)
}

function buildUrl(path: string, query: Record<string, unknown> = {}): URL {
  const url = new URL(BASE + path, window.location.origin)
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined && value !== null && value !== '') url.searchParams.set(key, String(value))
  }
  return url
}

function toApiError(status: number, data: { code?: string; detail?: string; errors?: ApiError['errors'] } | null, token: string | null) {
  if (status === 401 && token) handleUnauthorized()
  return new ApiError(status, data?.code ?? 'UNKNOWN', data?.detail ?? 'Beklenmeyen bir hata oluştu', data?.errors ?? [])
}

export async function api<T>(
  path: string,
  opts: {
    method?: string
    body?: unknown
    query?: Record<string, unknown>
    signal?: AbortSignal
  } = {},
): Promise<T> {
  const headers: Record<string, string> = {}
  const token = useAuthStore().token
  if (token) headers.Authorization = `Bearer ${token}`

  let body: BodyInit | undefined
  if (opts.body instanceof FormData) {
    body = opts.body
  } else if (opts.body !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(opts.body)
  }

  const res = await fetch(buildUrl(path, opts.query), { method: opts.method ?? 'GET', headers, body, signal: opts.signal })
  if (res.status === 204) return undefined as T

  const data = await res.json().catch(() => null)
  if (!res.ok) throw toApiError(res.status, data, token)
  return data as T
}

/** Dosya döndüren uçlar (ör. dışa aktarma): gövde Blob olarak, dosya adı Content-Disposition'dan gelir. */
export async function apiDownload(
  path: string,
  opts: { query?: Record<string, unknown> } = {},
): Promise<{ blob: Blob; filename: string | null }> {
  const token = useAuthStore().token
  const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {}

  const res = await fetch(buildUrl(path, opts.query), { headers })
  if (!res.ok) throw toApiError(res.status, await res.json().catch(() => null), token)
  return { blob: await res.blob(), filename: filenameFromDisposition(res.headers.get('Content-Disposition')) }
}
