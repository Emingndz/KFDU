import { type MaybeRefOrGetter, toValue } from 'vue'
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { api } from './client'
import type {
  DeleteAccountIn,
  EmailChangeIn,
  MeOut,
  MeUpdateIn,
  Page,
  ProfileOut,
  PublicUserOut,
  PublicUserWithFollowOut,
} from '@/types'

export function fetchMeRequest() {
  return api<MeOut>('/users/me')
}

export function updateMeRequest(payload: MeUpdateIn) {
  return api<MeOut>('/users/me', { method: 'PATCH', body: payload })
}

export function changeEmailRequest(payload: EmailChangeIn) {
  return api<MeOut>('/users/me/email', { method: 'PUT', body: payload })
}

export function deleteAccountRequest(payload: DeleteAccountIn) {
  return api<void>('/users/me', { method: 'DELETE', body: payload })
}

export function getProfileRequest(username: string) {
  return api<ProfileOut>(`/users/${username}`)
}

export function useProfile(username: MaybeRefOrGetter<string>) {
  return useQuery(() => ({
    queryKey: ['profile', toValue(username)],
    queryFn: () => getProfileRequest(toValue(username)),
    staleTime: 60_000,
  }))
}

export function getFollowersRequest(username: string, page = 1) {
  return api<Page<PublicUserWithFollowOut>>(`/users/${username}/followers`, { query: { page } })
}

export function getFollowingRequest(username: string, page = 1) {
  return api<Page<PublicUserWithFollowOut>>(`/users/${username}/following`, { query: { page } })
}

export function useFollowers(username: MaybeRefOrGetter<string>, enabled: MaybeRefOrGetter<boolean> = true) {
  return useInfiniteQuery(() => ({
    queryKey: ['followers', toValue(username)],
    queryFn: ({ pageParam }: { pageParam: number }) => getFollowersRequest(toValue(username), pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage: Page<PublicUserWithFollowOut>) => (lastPage.has_next ? lastPage.page + 1 : undefined),
    enabled: toValue(enabled),
  }))
}

export function useFollowing(username: MaybeRefOrGetter<string>, enabled: MaybeRefOrGetter<boolean> = true) {
  return useInfiniteQuery(() => ({
    queryKey: ['following', toValue(username)],
    queryFn: ({ pageParam }: { pageParam: number }) => getFollowingRequest(toValue(username), pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage: Page<PublicUserWithFollowOut>) => (lastPage.has_next ? lastPage.page + 1 : undefined),
    enabled: toValue(enabled),
  }))
}

export function uploadAvatarRequest(file: File) {
  const form = new FormData()
  form.append('file', file)
  return api<{ avatar_url: string }>('/users/me/avatar', { method: 'POST', body: form })
}

export function removeAvatarRequest() {
  return api<{ avatar_url: null }>('/users/me/avatar', { method: 'DELETE' })
}

export function useUploadAvatar() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: uploadAvatarRequest,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['user', 'me'] }),
  })
}

export function useRemoveAvatar() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: removeAvatarRequest,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['user', 'me'] }),
  })
}

export function followUserRequest(username: string) {
  return api<{ following: boolean; followers_count: number }>(`/users/${username}/follow`, { method: 'POST' })
}

export function unfollowUserRequest(username: string) {
  return api<{ following: boolean; followers_count: number }>(`/users/${username}/follow`, { method: 'DELETE' })
}

export function searchUsersRequest(q: string, page = 1) {
  return api<Page<PublicUserOut>>('/users/search', { query: { q, page } })
}

export function getSuggestionsRequest(limit = 10) {
  return api<PublicUserOut[]>('/users/suggestions', { query: { limit } })
}

export function useMe() {
  return useQuery({ queryKey: ['user', 'me'], queryFn: fetchMeRequest })
}

export function useUpdateMe() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: updateMeRequest,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['user', 'me'] }),
  })
}

export function useSuggestions(limit = 10) {
  return useQuery({ queryKey: ['user-suggestions', limit], queryFn: () => getSuggestionsRequest(limit) })
}

export function useUserSearch(q: MaybeRefOrGetter<string>) {
  return useInfiniteQuery(() => ({
    queryKey: ['user-search', toValue(q)],
    queryFn: ({ pageParam }: { pageParam: number }) => searchUsersRequest(toValue(q), pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage: Page<PublicUserOut>) => (lastPage.has_next ? lastPage.page + 1 : undefined),
    enabled: toValue(q).trim().length >= 2,
    staleTime: 5 * 60_000,
  }))
}

function invalidateFollowRelated(queryClient: ReturnType<typeof useQueryClient>, username: string) {
  void queryClient.invalidateQueries({ queryKey: ['profile', username] })
  void queryClient.invalidateQueries({ queryKey: ['followers', username] })
  void queryClient.invalidateQueries({ queryKey: ['following'] })
  void queryClient.invalidateQueries({ queryKey: ['user-suggestions'] })
  void queryClient.invalidateQueries({ queryKey: ['user-search'] })
}

export function useFollowUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: followUserRequest,
    onSuccess: (_, username) => invalidateFollowRelated(queryClient, username),
  })
}

export function useUnfollowUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: unfollowUserRequest,
    onSuccess: (_, username) => invalidateFollowRelated(queryClient, username),
  })
}
