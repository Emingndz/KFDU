import { computed, type MaybeRefOrGetter, ref, toValue } from 'vue'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { toast } from 'vue-sonner'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { upsertEntryRequest } from '@/api/library'
import type { CatalogContentType } from '@/api/catalog'
import type { EntryUpdateIn, LibraryStatus } from '@/types'

interface OptimisticState {
  status: LibraryStatus | null
  rating: number | null
  is_favorite: boolean
}

export function useContentActions(
  type: CatalogContentType,
  externalId: MaybeRefOrGetter<string>,
  initial?: MaybeRefOrGetter<Partial<OptimisticState> | undefined>,
) {
  const auth = useAuthStore()
  const router = useRouter()
  const queryClient = useQueryClient()

  const overlay = ref<OptimisticState | null>(null)

  const status = computed<LibraryStatus | null>(() => overlay.value?.status ?? toValue(initial)?.status ?? null)
  const rating = computed<number | null>(() => overlay.value?.rating ?? toValue(initial)?.rating ?? null)
  const isFavorite = computed<boolean>(() => overlay.value?.is_favorite ?? toValue(initial)?.is_favorite ?? false)

  function requireAuth(): boolean {
    if (auth.isAuthenticated) return true
    toast.info('Bunun için giriş yapmalısın')
    void router.push({ path: '/giris', query: { redirect: router.currentRoute.value.fullPath } })
    return false
  }

  function invalidateRelated() {
    const id = toValue(externalId)
    void queryClient.invalidateQueries({ queryKey: ['content-state', type, id] })
    if (auth.me) {
      void queryClient.invalidateQueries({ queryKey: ['library', auth.me.username] })
      void queryClient.invalidateQueries({ queryKey: ['user-summary', auth.me.username] })
    }
    void queryClient.invalidateQueries({ queryKey: ['recs', type] })
  }

  const mutation = useMutation({
    mutationFn: (payload: EntryUpdateIn) => upsertEntryRequest(type, toValue(externalId), payload),
    onSettled: invalidateRelated,
  })

  async function apply(payload: EntryUpdateIn) {
    if (!requireAuth()) return
    const previous: OptimisticState = { status: status.value, rating: rating.value, is_favorite: isFavorite.value }
    overlay.value = {
      status: payload.status !== undefined ? payload.status : previous.status,
      rating: payload.rating !== undefined ? payload.rating : previous.rating,
      is_favorite: payload.is_favorite ?? previous.is_favorite,
    }
    try {
      await mutation.mutateAsync(payload)
    } catch {
      overlay.value = previous
      toast.error('Bir şeyler ters gitti, tekrar dene')
    }
  }

  function setStatus(next: LibraryStatus) {
    void apply({ status: status.value === next ? null : next })
  }

  function setRating(next: number | null) {
    // StarRating aynı değere tıklayınca zaten kendi içinde null yayar (bkz. F3.1) — burada
    // ikinci bir eşitlik kontrolü yapmıyoruz, StarRating'in kararını olduğu gibi uyguluyoruz.
    void apply({ rating: next })
  }

  function toggleFavorite() {
    void apply({ is_favorite: !isFavorite.value })
  }

  return {
    status,
    rating,
    isFavorite,
    setStatus,
    setRating,
    toggleFavorite,
    isPending: mutation.isPending,
  }
}
