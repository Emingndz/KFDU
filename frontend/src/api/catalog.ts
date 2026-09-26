import { useQuery } from '@tanstack/vue-query'
import { api } from './client'
import type { GenreOut } from '@/types'

export type CatalogContentType = 'movie' | 'tv' | 'book'

export function getGenresRequest(type: CatalogContentType) {
  return api<GenreOut[]>('/catalog/genres', { query: { type } })
}

export function useGenres(type: CatalogContentType) {
  return useQuery({ queryKey: ['genres', type], queryFn: () => getGenresRequest(type) })
}
