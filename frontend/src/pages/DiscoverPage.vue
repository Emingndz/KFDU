<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDebounce, useIntersectionObserver } from '@vueuse/core'
import { Search, X } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import {
  type CatalogContentType,
  type DiscoverFilters,
  useCollection,
  useDiscover,
  useGenres,
  useSearch,
  useTrending,
} from '@/api/catalog'
import { usePlatformPopular, usePlatformTopRated } from '@/api/stats'
import { useFollowUser, useUnfollowUser, useUserSearch } from '@/api/users'
import { useLibraryLookup } from '@/api/library'
import { useAuthStore } from '@/stores/auth'
import { contentKey } from '@/utils/content'
import ContentGrid from '@/components/content/ContentGrid.vue'
import ContentRow from '@/components/content/ContentRow.vue'
import FilterPanel from '@/components/content/FilterPanel.vue'
import UserCard from '@/components/users/UserCard.vue'
import BaseSpinner from '@/components/ui/BaseSpinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'

type DiscoverTab = 'film' | 'kitap' | 'kullanici'

const TAB_TYPE: Record<'film' | 'kitap', CatalogContentType> = { film: 'movie', kitap: 'book' }

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

function readQueryValue(key: string): string | undefined {
  const value = route.query[key]
  return typeof value === 'string' && value.length > 0 ? value : undefined
}

const tab = ref<DiscoverTab>((readQueryValue('tur') as DiscoverTab | undefined) ?? 'film')
const searchText = ref(readQueryValue('q') ?? '')
const filters = ref<DiscoverFilters>({
  genre: readQueryValue('tur_id'),
  year_from: readQueryValue('yil_min') ? Number(readQueryValue('yil_min')) : undefined,
  year_to: readQueryValue('yil_max') ? Number(readQueryValue('yil_max')) : undefined,
  min_rating: readQueryValue('puan_min') ? Number(readQueryValue('puan_min')) : undefined,
  sort: readQueryValue('sirala') ?? 'popular',
  language: readQueryValue('dil'),
})

const debouncedQ = useDebounce(searchText, 350)
const contentType = computed<CatalogContentType>(() => TAB_TYPE[tab.value === 'kullanici' ? 'film' : tab.value])
const hasSearch = computed(() => debouncedQ.value.trim().length > 0)
const hasActiveFilters = computed(() => {
  const f = filters.value
  return Boolean(f.genre || f.year_from || f.year_to || f.min_rating || (f.language && f.language.length > 0))
})

watch([tab, debouncedQ, filters], () => {
  const query: Record<string, string> = {}
  if (debouncedQ.value.trim()) query.q = debouncedQ.value.trim()
  if (tab.value !== 'film') query.tur = tab.value
  const f = filters.value
  if (f.genre) query.tur_id = f.genre
  if (f.year_from) query.yil_min = String(f.year_from)
  if (f.year_to) query.yil_max = String(f.year_to)
  if (f.min_rating) query.puan_min = String(f.min_rating)
  if (f.sort && f.sort !== 'popular') query.sirala = f.sort
  if (f.language) query.dil = f.language
  void router.replace({ query })
}, { deep: true })

function clearSearch() {
  searchText.value = ''
}

// İçerik araması (film/kitap, arama metni varken)
const contentSearch = useSearch(contentType, debouncedQ)
// İçerik keşfi (film/kitap, filtre varken ama arama yokken)
const contentDiscover = useDiscover(contentType, filters)
// Kullanıcı araması
const userSearch = useUserSearch(debouncedQ)

const showingUserSearch = computed(() => tab.value === 'kullanici')
const showingContentSearch = computed(() => !showingUserSearch.value && hasSearch.value)
const showingContentDiscover = computed(() => !showingUserSearch.value && !hasSearch.value && hasActiveFilters.value)

const contentItems = computed(() => {
  const source = showingContentSearch.value ? contentSearch : showingContentDiscover.value ? contentDiscover : null
  return source?.data.value?.pages.flatMap((p) => p.items) ?? []
})
const contentIsPending = computed(() =>
  showingContentSearch.value ? contentSearch.isPending.value : contentDiscover.isPending.value,
)
const contentIsError = computed(() =>
  showingContentSearch.value ? contentSearch.isError.value : contentDiscover.isError.value,
)
const contentHasNextPage = computed(() =>
  showingContentSearch.value ? Boolean(contentSearch.hasNextPage.value) : Boolean(contentDiscover.hasNextPage.value),
)
const contentIsFetchingNext = computed(() =>
  showingContentSearch.value ? contentSearch.isFetchingNextPage.value : contentDiscover.isFetchingNextPage.value,
)

function fetchMoreContent() {
  if (showingContentSearch.value) void contentSearch.fetchNextPage()
  else void contentDiscover.fetchNextPage()
}

const lookupKeys = computed(() => contentItems.value.map((item) => contentKey(item.type, item.external_id)))
const libraryLookup = useLibraryLookup(lookupKeys)

// Vitrinler (arama/filtre yokken)
const topRated = usePlatformTopRated(contentType)
const popular = usePlatformPopular(contentType)
const trending = useTrending(contentType)
const nowPlaying = useCollection('now_playing')
const upcoming = useCollection('upcoming')
const trendingBooks = useTrending('book')
const browseGenres = useGenres(contentType)

function browseGenre(genreKey: string) {
  filters.value = { ...filters.value, genre: genreKey }
}

// Kullanıcı araması takip et/bırak
// Not: PublicUserOut (arama sonucu) is_following bilgisi taşımıyor (yalnız ProfileOut/
// PublicUserWithFollowOut taşıyor) — bu yüzden önceden takip edilen kullanıcılar başlangıçta
// "Takip et" gösterir; tıklanınca bu oturum için yerel olarak işaretlenir (follow zaten idempotent).
const followMutation = useFollowUser()
const unfollowMutation = useUnfollowUser()
const followPendingUsername = ref<string | null>(null)
const followedThisSession = ref(new Set<string>())

async function toggleFollow(username: string) {
  if (!auth.isAuthenticated) {
    toast.info('Bunun için giriş yapmalısın')
    void router.push({ path: '/giris', query: { redirect: route.fullPath } })
    return
  }
  const isFollowing = followedThisSession.value.has(username)
  followPendingUsername.value = username
  try {
    if (isFollowing) {
      await unfollowMutation.mutateAsync(username)
      followedThisSession.value.delete(username)
    } else {
      await followMutation.mutateAsync(username)
      followedThisSession.value.add(username)
    }
  } catch {
    toast.error('Bir şeyler ters gitti, tekrar dene')
  } finally {
    followPendingUsername.value = null
  }
}

const userItems = computed(() => userSearch.data.value?.pages.flatMap((p) => p.items) ?? [])

const sentinelRef = ref<HTMLElement | null>(null)
useIntersectionObserver(sentinelRef, ([entry]) => {
  if (!entry?.isIntersecting) return
  if (showingUserSearch.value) {
    if (userSearch.hasNextPage.value && !userSearch.isFetchingNextPage.value) void userSearch.fetchNextPage()
  } else if (contentHasNextPage.value && !contentIsFetchingNext.value) {
    fetchMoreContent()
  }
})
</script>

<template>
  <div class="flex flex-col gap-6 py-6">
    <div class="flex flex-col gap-3">
      <div class="relative">
        <Search class="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted" />
        <input
          v-model="searchText"
          type="search"
          placeholder="Film, kitap veya kullanıcı ara…"
          class="h-12 w-full rounded-lg border border-border bg-surface pr-10 pl-10 text-sm text-fg placeholder:text-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
        />
        <button
          v-if="searchText"
          type="button"
          aria-label="Aramayı temizle"
          class="absolute top-1/2 right-3 flex size-6 -translate-y-1/2 items-center justify-center text-muted hover:text-fg"
          @click="clearSearch"
        >
          <X class="size-4" />
        </button>
      </div>

      <div class="flex gap-1 rounded-lg bg-surface-2 p-1">
        <button
          v-for="option in [
            { value: 'film', label: 'Film' },
            { value: 'kitap', label: 'Kitap' },
            { value: 'kullanici', label: 'Kullanıcı' },
          ]"
          :key="option.value"
          type="button"
          class="flex-1 rounded-md px-3 py-2 text-sm font-medium transition"
          :class="tab === option.value ? 'bg-surface text-fg shadow-sm' : 'text-muted hover:text-fg'"
          @click="tab = option.value as DiscoverTab"
        >
          {{ option.label }}
        </button>
      </div>

      <FilterPanel v-if="!showingUserSearch" v-model="filters" :type="contentType" />
    </div>

    <!-- Kullanıcı araması -->
    <template v-if="showingUserSearch">
      <p v-if="debouncedQ.trim().length < 2" class="text-sm text-muted">
        Kullanıcı aramak için en az 2 karakter yaz.
      </p>
      <div v-else-if="userSearch.isPending.value" class="flex justify-center py-8"><BaseSpinner /></div>
      <EmptyState v-else-if="userItems.length === 0" title="Kullanıcı bulunamadı" :message="`'${debouncedQ}' için sonuç yok.`" />
      <div v-else class="flex flex-col gap-2">
        <UserCard
          v-for="user in userItems"
          :key="user.username"
          :user="user"
          :is-following="followedThisSession.has(user.username)"
          :follow-pending="followPendingUsername === user.username"
          @toggle-follow="toggleFollow(user.username)"
        />
      </div>
    </template>

    <!-- İçerik araması / keşfi -->
    <template v-else-if="showingContentSearch || showingContentDiscover">
      <ErrorState
        v-if="contentIsError"
        message="Sonuçlar yüklenemedi."
        @retry="showingContentSearch ? contentSearch.refetch() : contentDiscover.refetch()"
      />
      <ContentGrid
        v-else
        :items="contentItems"
        :lookup="libraryLookup.data.value"
        :loading="contentIsPending"
        :empty-title="showingContentSearch ? 'Sonuç bulunamadı' : 'Sonuç yok'"
        :empty-message="showingContentSearch ? `'${debouncedQ}' için sonuç bulunamadı.` : 'Filtreleri değiştirip tekrar dene.'"
      />
      <div ref="sentinelRef" class="h-4" />
      <div v-if="contentIsFetchingNext" class="flex justify-center py-4"><BaseSpinner /></div>
    </template>

    <!-- Vitrinler -->
    <template v-else>
      <ContentRow
        title="Platformda En Yüksek Puanlılar"
        :items="topRated.data.value?.items ?? []"
        :loading="topRated.isPending.value"
      />
      <p v-if="!topRated.isPending.value && (topRated.data.value?.items.length ?? 0) === 0" class="text-sm text-muted">
        Henüz yeterli puan yok — ilk puanlayan sen ol!
      </p>

      <ContentRow title="Platformda En Popülerler" :items="popular.data.value ?? []" :loading="popular.isPending.value" />

      <template v-if="tab === 'film'">
        <ContentRow title="Haftanın Trend Filmleri" :items="trending.data.value ?? []" :loading="trending.isPending.value" />
        <ContentRow title="Vizyonda (Türkiye)" :items="nowPlaying.data.value ?? []" :loading="nowPlaying.isPending.value" />
        <ContentRow title="Yakında" :items="upcoming.data.value ?? []" :loading="upcoming.isPending.value" />
      </template>
      <template v-else>
        <ContentRow title="Trend Kitaplar" :items="trendingBooks.data.value ?? []" :loading="trendingBooks.isPending.value" />
      </template>

      <section class="flex flex-col gap-3">
        <h2 class="text-lg font-semibold text-fg">Türlere Göz At</h2>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="genre in browseGenres.data.value ?? []"
            :key="genre.key"
            type="button"
            class="rounded-full border border-border bg-surface px-3 py-1.5 text-sm text-fg hover:bg-surface-2"
            @click="browseGenre(genre.key)"
          >
            {{ genre.label }}
          </button>
        </div>
      </section>
    </template>
  </div>
</template>
