import { type MaybeRefOrGetter, toValue } from 'vue'
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { api } from './client'
import type { CatalogContentType } from './catalog'
import type { CommentOut, CursorPage, Page, ReviewDetail, ReviewOut } from '@/types'

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

export function listCommentsRequest(activityId: number, cursor?: string) {
  return api<CursorPage<CommentOut>>(`/activities/${activityId}/comments`, { query: { cursor } })
}

export function useComments(activityId: MaybeRefOrGetter<number>) {
  return useInfiniteQuery(() => ({
    queryKey: ['comments', toValue(activityId)],
    queryFn: ({ pageParam }: { pageParam: string | undefined }) => listCommentsRequest(toValue(activityId), pageParam),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage: CursorPage<CommentOut>) => lastPage.next_cursor ?? undefined,
    staleTime: 30_000,
  }))
}

export function addCommentRequest(activityId: number, body: string) {
  return api<CommentOut>(`/activities/${activityId}/comments`, { method: 'POST', body: { body } })
}

export function updateCommentRequest(commentId: number, body: string) {
  return api<CommentOut>(`/comments/${commentId}`, { method: 'PATCH', body: { body } })
}

export function deleteCommentRequest(commentId: number) {
  return api<void>(`/comments/${commentId}`, { method: 'DELETE' })
}

export function useAddComment(activityId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: string) => addCommentRequest(activityId, body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['comments', activityId] }),
  })
}

export function useUpdateComment(activityId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ commentId, body }: { commentId: number; body: string }) => updateCommentRequest(commentId, body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['comments', activityId] }),
  })
}

export function useDeleteComment(activityId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteCommentRequest,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['comments', activityId] }),
  })
}
