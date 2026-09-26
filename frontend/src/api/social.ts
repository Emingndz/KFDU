import { type MaybeRefOrGetter, toValue } from 'vue'
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { api } from './client'
import type { CatalogContentType } from './catalog'
import type { Page, ReviewDetail, ReviewOut } from '@/types'

export function listContentReviewsRequest(type: CatalogContentType, externalId: string, sort: 'new' | 'popular' = 'new', page = 1) {
  return api<Page<ReviewOut>>('/reviews', { query: { type, external_id: externalId, sort, page } })
}

export function useContentReviews(
  type: MaybeRefOrGetter<CatalogContentType>,
  externalId: MaybeRefOrGetter<string>,
  sort: MaybeRefOrGetter<'new' | 'popular'>,
) {
  return useInfiniteQuery(() => ({
    queryKey: ['reviews', toValue(type), toValue(externalId), toValue(sort)],
    queryFn: ({ pageParam }: { pageParam: number }) =>
      listContentReviewsRequest(toValue(type), toValue(externalId), toValue(sort), pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage: Page<ReviewOut>) => (lastPage.has_next ? lastPage.page + 1 : undefined),
    staleTime: 60_000,
  }))
}

export function getReviewDetailRequest(reviewId: number) {
  return api<ReviewDetail>(`/reviews/${reviewId}`)
}

export function useReviewDetail(reviewId: MaybeRefOrGetter<number | null>) {
  return useQuery(() => ({
    queryKey: ['review', toValue(reviewId)],
    queryFn: () => getReviewDetailRequest(toValue(reviewId) as number),
    enabled: toValue(reviewId) !== null,
    staleTime: 60_000,
  }))
}

export function likeActivityRequest(activityId: number) {
  return api<{ liked: boolean; likes_count: number }>(`/activities/${activityId}/like`, { method: 'POST' })
}

export function unlikeActivityRequest(activityId: number) {
  return api<{ liked: boolean; likes_count: number }>(`/activities/${activityId}/like`, { method: 'DELETE' })
}

export function useLikeActivity() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: likeActivityRequest,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['reviews'] }),
  })
}

export function useUnlikeActivity() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: unlikeActivityRequest,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['reviews'] }),
  })
}
