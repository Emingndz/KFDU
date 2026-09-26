import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
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
