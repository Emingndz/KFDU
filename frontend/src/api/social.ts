import { type MaybeRefOrGetter, toValue } from 'vue'
import { type InfiniteData, useInfiniteQuery, useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { toast } from 'vue-sonner'
import { api } from './client'
import { useAuthStore } from '@/stores/auth'
import type { CatalogContentType } from './catalog'
import type { ActivityOut, CommentOut, CursorPage, NotificationOut, Page, ReviewDetail, ReviewOut } from '@/types'

export type FeedScope = 'following' | 'global'

export function getFeedRequest(scope: FeedScope, cursor?: string, limit = 15) {
  return api<CursorPage<ActivityOut>>('/feed', { query: { scope, cursor, limit } })
}

export function useFeed(scope: MaybeRefOrGetter<FeedScope>) {
  return useInfiniteQuery(() => ({
    queryKey: ['feed', toValue(scope)],
    queryFn: ({ pageParam }: { pageParam: string | undefined }) => getFeedRequest(toValue(scope), pageParam),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage: CursorPage<ActivityOut>) => lastPage.next_cursor ?? undefined,
    staleTime: 30_000,
  }))
}

function patchFeedCaches(
  queryClient: ReturnType<typeof useQueryClient>,
  activityId: number,
  patch: (activity: ActivityOut) => ActivityOut,
) {
  queryClient.setQueriesData<InfiniteData<CursorPage<ActivityOut>>>({ queryKey: ['feed'] }, (data) => {
    if (!data) return data
    return {
      ...data,
      pages: data.pages.map((page) => ({
        ...page,
        items: page.items.map((item) => (item.id === activityId ? patch(item) : item)),
      })),
    }
  })
}

export function useLike() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ activityId, liked }: { activityId: number; liked: boolean }) =>
      liked ? likeActivityRequest(activityId) : unlikeActivityRequest(activityId),
    onMutate: async ({ activityId, liked }) => {
      await queryClient.cancelQueries({ queryKey: ['feed'] })
      const previous = queryClient.getQueriesData<InfiniteData<CursorPage<ActivityOut>>>({ queryKey: ['feed'] })
      patchFeedCaches(queryClient, activityId, (activity) => ({
        ...activity,
        liked_by_me: liked,
        likes_count: activity.likes_count + (liked ? 1 : -1),
      }))
      return { previous }
    },
    onError: (_error, _vars, context) => {
      context?.previous.forEach(([key, data]) => queryClient.setQueryData(key, data))
      toast.error('Bir şeyler ters gitti')
    },
  })
}

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

export function getUserActivitiesRequest(username: string, cursor?: string, limit = 15) {
  return api<CursorPage<ActivityOut>>(`/users/${username}/activities`, { query: { cursor, limit } })
}

export function useUserActivities(username: MaybeRefOrGetter<string>) {
  return useInfiniteQuery(() => ({
    queryKey: ['user-activities', toValue(username)],
    queryFn: ({ pageParam }: { pageParam: string | undefined }) => getUserActivitiesRequest(toValue(username), pageParam),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage: CursorPage<ActivityOut>) => lastPage.next_cursor ?? undefined,
    staleTime: 30_000,
  }))
}

export function getUserReviewsRequest(username: string, page = 1) {
  return api<Page<ReviewOut>>(`/users/${username}/reviews`, { query: { page } })
}

export function useUserReviews(username: MaybeRefOrGetter<string>) {
  return useInfiniteQuery(() => ({
    queryKey: ['user-reviews', toValue(username)],
    queryFn: ({ pageParam }: { pageParam: number }) => getUserReviewsRequest(toValue(username), pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage: Page<ReviewOut>) => (lastPage.has_next ? lastPage.page + 1 : undefined),
    staleTime: 60_000,
  }))
}

export function listNotificationsRequest(cursor?: string, limit = 20) {
  return api<CursorPage<NotificationOut>>('/notifications', { query: { cursor, limit } })
}

export function useNotifications() {
  const auth = useAuthStore()
  return useInfiniteQuery(() => ({
    queryKey: ['notifications'],
    queryFn: ({ pageParam }: { pageParam: string | undefined }) => listNotificationsRequest(pageParam),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage: CursorPage<NotificationOut>) => lastPage.next_cursor ?? undefined,
    enabled: auth.isAuthenticated,
    staleTime: 30_000,
  }))
}

export function getUnreadNotificationsCountRequest() {
  return api<{ count: number }>('/notifications/unread-count')
}

export function useUnreadNotificationsCount() {
  const auth = useAuthStore()
  return useQuery(() => ({
    queryKey: ['notifications', 'unread-count'],
    queryFn: getUnreadNotificationsCountRequest,
    enabled: auth.isAuthenticated,
    refetchInterval: 60_000,
    staleTime: 30_000,
  }))
}

export function markAllNotificationsReadRequest() {
  return api<void>('/notifications/read-all', { method: 'POST' })
}

export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: markAllNotificationsReadRequest,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  })
}

export function markNotificationReadRequest(notificationId: number) {
  return api<void>(`/notifications/${notificationId}/read`, { method: 'POST' })
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: markNotificationReadRequest,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  })
}
