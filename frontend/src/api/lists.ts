import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { type MaybeRefOrGetter, toValue } from 'vue'
import { api } from './client'
import { useAuthStore } from '@/stores/auth'
import type { CatalogContentType } from './catalog'
import type {
  ListCreateIn,
  ListDetail,
  ListItemIn,
  ListItemOut,
  ListOut,
  ListUpdateIn,
  MyListOut,
  Page,
} from '@/types'

export function createListRequest(payload: ListCreateIn) {
  return api<ListOut>('/lists', { method: 'POST', body: payload })
}

export function getMyListsRequest(params: { type?: CatalogContentType; external_id?: string } = {}) {
  return api<MyListOut[]>('/lists/mine', { query: params })
}

export function getListDetailRequest(listId: number) {
  return api<ListDetail>(`/lists/${listId}`)
}

export function updateListRequest(listId: number, payload: ListUpdateIn) {
  return api<ListOut>(`/lists/${listId}`, { method: 'PATCH', body: payload })
}

export function deleteListRequest(listId: number) {
  return api<void>(`/lists/${listId}`, { method: 'DELETE' })
}

export function addListItemRequest(listId: number, payload: ListItemIn) {
  return api<ListItemOut>(`/lists/${listId}/items`, { method: 'POST', body: payload })
}

export function updateListItemNoteRequest(listId: number, contentId: number, note: string | null) {
  return api<ListItemOut>(`/lists/${listId}/items/${contentId}`, { method: 'PATCH', body: { note } })
}

export function removeListItemRequest(listId: number, contentId: number) {
  return api<void>(`/lists/${listId}/items/${contentId}`, { method: 'DELETE' })
}

export function reorderListItemsRequest(listId: number, contentIds: number[]) {
  return api<void>(`/lists/${listId}/order`, { method: 'PUT', body: { content_ids: contentIds } })
}

export function getUserListsRequest(username: string, page = 1) {
  return api<Page<ListOut>>(`/users/${username}/lists`, { query: { page } })
}

export function useMyLists(type: CatalogContentType, externalId: MaybeRefOrGetter<string>) {
  const auth = useAuthStore()
  return useQuery(() => ({
    queryKey: ['lists', 'mine', type, toValue(externalId)],
    queryFn: () => getMyListsRequest({ type, external_id: toValue(externalId) }),
    enabled: auth.isAuthenticated,
  }))
}

export function useAddListItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ listId, payload }: { listId: number; payload: ListItemIn }) => addListItemRequest(listId, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['lists'] }),
  })
}

export function useRemoveListItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ listId, contentId }: { listId: number; contentId: number }) => removeListItemRequest(listId, contentId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['lists'] }),
  })
}

export function useCreateList() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createListRequest,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['lists'] }),
  })
}

export function useListDetail(listId: MaybeRefOrGetter<number>) {
  return useQuery(() => ({
    queryKey: ['lists', 'detail', toValue(listId)],
    queryFn: () => getListDetailRequest(toValue(listId)),
    staleTime: 30_000,
  }))
}

export function useUpdateList() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ listId, payload }: { listId: number; payload: ListUpdateIn }) => updateListRequest(listId, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['lists'] }),
  })
}

export function useDeleteList() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteListRequest,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['lists'] }),
  })
}

export function useUpdateListItemNote() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ listId, contentId, note }: { listId: number; contentId: number; note: string | null }) =>
      updateListItemNoteRequest(listId, contentId, note),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['lists'] }),
  })
}

export function useReorderListItems() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ listId, contentIds }: { listId: number; contentIds: number[] }) => reorderListItemsRequest(listId, contentIds),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['lists'] }),
  })
}
