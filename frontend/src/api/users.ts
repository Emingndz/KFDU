import { type MaybeRefOrGetter, toValue } from 'vue'
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { api } from './client'
import type { DeleteAccountIn, EmailChangeIn, MeOut, MeUpdateIn, Page, ProfileOut, PublicUserOut } from '@/types'

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
  void queryClient.invalidateQueries({ queryKey: ['user', username] })
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
