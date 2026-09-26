import { type MaybeRefOrGetter, toValue } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { api } from './client'
import type { CatalogContentType } from './catalog'
import type { ContentSummary, Page } from '@/types'

export function getTopRatedRequest(type?: CatalogContentType, limit = 20) {
  return api<Page<ContentSummary>>('/platform/top-rated', { query: { type, limit } })
}

export function usePlatformTopRated(type: MaybeRefOrGetter<CatalogContentType | undefined>) {
  return useQuery(() => ({
    queryKey: ['showcase', 'top-rated', toValue(type)],
    queryFn: () => getTopRatedRequest(toValue(type)),
    staleTime: 10 * 60_000,
  }))
}

export function getPopularRequest(type?: CatalogContentType, days = 30, limit = 20) {
  return api<ContentSummary[]>('/platform/popular', { query: { type, days, limit } })
}

export function usePlatformPopular(type: MaybeRefOrGetter<CatalogContentType | undefined>) {
  return useQuery(() => ({
    queryKey: ['showcase', 'popular', toValue(type)],
    queryFn: () => getPopularRequest(toValue(type)),
    staleTime: 10 * 60_000,
  }))
}
