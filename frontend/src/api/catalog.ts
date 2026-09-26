import { type MaybeRefOrGetter, toValue } from 'vue'
import { useInfiniteQuery, useQuery } from '@tanstack/vue-query'
import { api } from './client'
import type { ContentSummary, GenreOut, Page } from '@/types'

export type CatalogContentType = 'movie' | 'tv' | 'book'

export interface DiscoverFilters {
  genre?: string
  year_from?: number
  year_to?: number
  min_rating?: number
  sort?: string
  language?: string
}

export function getGenresRequest(type: CatalogContentType) {
  return api<GenreOut[]>('/catalog/genres', { query: { type } })
}

export function useGenres(type: MaybeRefOrGetter<CatalogContentType>) {
  return useQuery(() => ({
    queryKey: ['genres', toValue(type)],
    queryFn: () => getGenresRequest(toValue(type)),
    staleTime: 60 * 60_000,
  }))
}

export function searchContentRequest(type: CatalogContentType, q: string, page = 1) {
  return api<Page<ContentSummary>>('/catalog/search', { query: { type, q, page } })
}

export function useSearch(type: MaybeRefOrGetter<CatalogContentType>, q: MaybeRefOrGetter<string>) {
  return useInfiniteQuery(() => ({
    queryKey: ['search', toValue(type), toValue(q)],
    queryFn: ({ pageParam }: { pageParam: number }) => searchContentRequest(toValue(type), toValue(q), pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage: Page<ContentSummary>) => (lastPage.has_next ? lastPage.page + 1 : undefined),
    enabled: toValue(q).trim().length > 0,
    staleTime: 5 * 60_000,
  }))
}

export function discoverContentRequest(type: CatalogContentType, filters: DiscoverFilters, page = 1) {
  return api<Page<ContentSummary>>('/catalog/discover', { query: { type, ...filters, page } })
}

export function useDiscover(type: MaybeRefOrGetter<CatalogContentType>, filters: MaybeRefOrGetter<DiscoverFilters>) {
  return useInfiniteQuery(() => ({
    queryKey: ['discover', toValue(type), toValue(filters)],
    queryFn: ({ pageParam }: { pageParam: number }) => discoverContentRequest(toValue(type), toValue(filters), pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage: Page<ContentSummary>) => (lastPage.has_next ? lastPage.page + 1 : undefined),
    staleTime: 10 * 60_000,
  }))
}

export function trendingContentRequest(type: CatalogContentType) {
  return api<ContentSummary[]>('/catalog/trending', { query: { type } })
}

export function useTrending(type: MaybeRefOrGetter<CatalogContentType>) {
  return useQuery(() => ({
    queryKey: ['showcase', 'trending', toValue(type)],
    queryFn: () => trendingContentRequest(toValue(type)),
    staleTime: 10 * 60_000,
  }))
}

export function collectionRequest(name: string) {
  return api<ContentSummary[]>(`/catalog/collections/${name}`)
}

export function useCollection(name: string) {
  return useQuery({
    queryKey: ['showcase', 'collection', name],
    queryFn: () => collectionRequest(name),
    staleTime: 10 * 60_000,
  })
}
