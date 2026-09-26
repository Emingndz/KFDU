import { type MaybeRefOrGetter, toValue } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { api } from './client'
import { useAuthStore } from '@/stores/auth'
import type { CatalogContentType } from './catalog'
import type {
  ContentState,
  EntryOut,
  EntryUpdateIn,
  LookupEntryOut,
  Page,
  ReviewBasicOut,
  ReviewCreateIn,
  ReviewUpdateIn,
} from '@/types'

export function upsertEntryRequest(type: CatalogContentType, externalId: string, payload: EntryUpdateIn) {
  return api<EntryOut>(`/library/${type}/${externalId}`, { method: 'PUT', body: payload })
}

export function deleteEntryRequest(type: CatalogContentType, externalId: string) {
  return api<void>(`/library/${type}/${externalId}`, { method: 'DELETE' })
}

export function getContentStateRequest(type: CatalogContentType, externalId: string) {
  return api<ContentState>(`/library/${type}/${externalId}/state`)
}

export function lookupLibraryRequest(keys: string[]) {
  return api<Record<string, LookupEntryOut>>('/library/lookup', { method: 'POST', body: { keys } })
}

export function useLibraryLookup(keys: MaybeRefOrGetter<string[]>) {
  const auth = useAuthStore()
  return useQuery(() => ({
    queryKey: ['library-lookup', toValue(keys)],
    queryFn: () => lookupLibraryRequest(toValue(keys)),
    enabled: auth.isAuthenticated && toValue(keys).length > 0,
    staleTime: 30_000,
  }))
}

export function getUserLibraryRequest(
  username: string,
  params: {
    type?: CatalogContentType
    status?: string
    favorite?: boolean
    sort?: string
    page?: number
    page_size?: number
  } = {},
) {
  return api<Page<EntryOut>>(`/users/${username}/library`, { query: params })
}

export function createReviewRequest(payload: ReviewCreateIn) {
  return api<ReviewBasicOut>('/reviews', { method: 'POST', body: payload })
}

export function updateReviewRequest(reviewId: number, payload: ReviewUpdateIn) {
  return api<ReviewBasicOut>(`/reviews/${reviewId}`, { method: 'PATCH', body: payload })
}

export function deleteReviewRequest(reviewId: number) {
  return api<void>(`/reviews/${reviewId}`, { method: 'DELETE' })
}
