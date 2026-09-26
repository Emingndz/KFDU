import { toast } from 'vue-sonner'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

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

export async function api<T>(
  path: string,
  opts: {
    method?: string
    body?: unknown
    query?: Record<string, unknown>
    signal?: AbortSignal
  } = {},
): Promise<T> {
  const url = new URL(BASE + path, window.location.origin)
  for (const [key, value] of Object.entries(opts.query ?? {})) {
    if (value !== undefined && value !== null && value !== '') url.searchParams.set(key, String(value))
  }

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

  const res = await fetch(url, { method: opts.method ?? 'GET', headers, body, signal: opts.signal })
  if (res.status === 204) return undefined as T

  const data = await res.json().catch(() => null)
  if (!res.ok) {
    if (res.status === 401 && token) handleUnauthorized()
    throw new ApiError(
      res.status,
      data?.code ?? 'UNKNOWN',
      data?.detail ?? 'Beklenmeyen bir hata oluştu',
      data?.errors ?? [],
    )
  }
  return data as T
}
