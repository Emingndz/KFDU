<script setup lang="ts">
import { computed, defineAsyncComponent, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { ApiError } from '@/api/client'
import { useFollowUser, useProfile, useUnfollowUser } from '@/api/users'
import { useProfileSummary, useUserStats } from '@/api/stats'
import { getUserLibraryRequest } from '@/api/library'
import { useUserActivities, useUserReviews } from '@/api/social'
import { getUserListsRequest } from '@/api/lists'
import { useQuery } from '@tanstack/vue-query'
import { useAuthStore } from '@/stores/auth'
import type { CatalogContentType } from '@/api/catalog'
import type { EntryOut, LookupEntryOut } from '@/types'
import { contentKey } from '@/utils/content'
import BaseTabs from '@/components/ui/BaseTabs.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import BaseSpinner from '@/components/ui/BaseSpinner.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import ProfileHeader from '@/components/users/ProfileHeader.vue'
import EditProfileModal from '@/components/users/EditProfileModal.vue'
import UserListModal from '@/components/users/UserListModal.vue'
import ActivityCard from '@/components/content/ActivityCard.vue'
import ContentGrid from '@/components/content/ContentGrid.vue'
import ReviewItem from '@/components/content/ReviewItem.vue'
import ListCard from '@/components/lists/ListCard.vue'
import ListFormModal from '@/components/lists/ListFormModal.vue'

const StatsCharts = defineAsyncComponent(() => import('@/components/stats/StatsCharts.vue'))

const props = defineProps<{ username: string }>()

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const profile = useProfile(() => props.username)
const summary = useProfileSummary(() => props.username)

const is404 = computed(() => profile.isError.value && profile.error.value instanceof ApiError && profile.error.value.status === 404)

watch(
  () => profile.data.value,
  (p) => {
    if (p) document.title = `${p.display_name || p.username} (@${p.username}) · KFDU`
  },
)

type TabKey = 'aktiviteler' | 'kutuphane' | 'puanlar' | 'incelemeler' | 'listeler' | 'favoriler' | 'istatistik'
const tab = ref<TabKey>((route.query.sekme as TabKey) || 'aktiviteler')
watch(tab, () => void router.replace({ query: { ...route.query, sekme: tab.value } }))

const TABS = [
  { value: 'aktiviteler', label: 'Aktiviteler' },
  { value: 'kutuphane', label: 'Kütüphane' },
  { value: 'puanlar', label: 'Puanlar' },
  { value: 'incelemeler', label: 'İncelemeler' },
  { value: 'listeler', label: 'Listeler' },
  { value: 'favoriler', label: 'Favoriler' },
  { value: 'istatistik', label: 'İstatistik' },
]

// İstatistik
const currentYear = new Date().getFullYear()
const statsYear = ref(String(currentYear))
const YEAR_OPTIONS = Array.from({ length: 5 }, (_, i) => {
  const y = currentYear - i
  return { value: String(y), label: String(y) }
})
const stats = useUserStats(
  () => props.username,
  () => Number(statsYear.value),
)

// Aktiviteler
const activities = useUserActivities(() => props.username)
const activityItems = computed(() => activities.data.value?.pages.flatMap((p) => p.items) ?? [])

// Kütüphane
const LIBRARY_FILTERS = [
  { key: 'izlenen', label: 'İzlediklerim', types: ['movie', 'tv'] as CatalogContentType[], status: 'completed' },
  { key: 'izlenecek', label: 'İzlenecekler', types: ['movie', 'tv'] as CatalogContentType[], status: 'planned' },
  { key: 'izleniyor', label: 'İzliyorum', types: ['movie', 'tv'] as CatalogContentType[], status: 'in_progress' },
  { key: 'okunan', label: 'Okuduklarım', types: ['book'] as CatalogContentType[], status: 'completed' },
  { key: 'okunacak', label: 'Okunacaklar', types: ['book'] as CatalogContentType[], status: 'planned' },
  { key: 'okunuyor', label: 'Okuyorum', types: ['book'] as CatalogContentType[], status: 'in_progress' },
  { key: 'yarim', label: 'Yarım Bıraktıklarım', types: [] as CatalogContentType[], status: 'dropped' },
]
const librarySubTab = ref(LIBRARY_FILTERS[0]!.key)
const librarySort = ref<'recent' | 'rating' | 'title' | 'year'>('recent')

const activeLibraryFilter = computed(() => LIBRARY_FILTERS.find((f) => f.key === librarySubTab.value)!)

function entriesToGridProps(entries: EntryOut[]) {
  const lookup: Record<string, LookupEntryOut> = {}
  for (const entry of entries) {
    lookup[contentKey(entry.content.type, entry.content.external_id)] = {
      status: entry.status,
      rating: entry.rating,
      is_favorite: entry.is_favorite,
    }
  }
  return { items: entries.map((e) => e.content), lookup }
}

function sortEntries(entries: EntryOut[], sort: typeof librarySort.value): EntryOut[] {
  const sorted = [...entries]
  if (sort === 'rating') sorted.sort((a, b) => (b.rating ?? -1) - (a.rating ?? -1))
  else if (sort === 'title') sorted.sort((a, b) => a.content.title.localeCompare(b.content.title, 'tr'))
  else if (sort === 'year') sorted.sort((a, b) => (b.content.year ?? 0) - (a.content.year ?? 0))
  else sorted.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
  return sorted
}

const libraryQueryA = useQuery(() => ({
  queryKey: ['profile-library', props.username, activeLibraryFilter.value.key, librarySort.value, 'a'],
  queryFn: () =>
    getUserLibraryRequest(props.username, {
      type: activeLibraryFilter.value.types[0],
      status: activeLibraryFilter.value.status,
      sort: librarySort.value,
      page_size: 60,
    }),
}))
const libraryQueryB = useQuery(() => ({
  queryKey: ['profile-library', props.username, activeLibraryFilter.value.key, librarySort.value, 'b'],
  queryFn: () =>
    getUserLibraryRequest(props.username, {
      type: activeLibraryFilter.value.types[1],
      status: activeLibraryFilter.value.status,
      sort: librarySort.value,
      page_size: 60,
    }),
  enabled: activeLibraryFilter.value.types.length > 1,
}))
const libraryIsMulti = computed(() => activeLibraryFilter.value.types.length > 1)
const libraryIsPending = computed(() => libraryQueryA.isPending.value || (libraryIsMulti.value && libraryQueryB.isPending.value))
const libraryGrid = computed(() => {
  const a = libraryQueryA.data.value?.items ?? []
  const b = libraryQueryB.data.value?.items ?? []
  const merged = libraryIsMulti.value ? sortEntries([...a, ...b], librarySort.value) : a
  return entriesToGridProps(merged)
})

// Puanlar
const ratingsQuery = useQuery(() => ({
  queryKey: ['profile-ratings', props.username],
  queryFn: () => getUserLibraryRequest(props.username, { sort: 'rating', page_size: 60 }),
}))
const ratingsGrid = computed(() => {
  const rated = (ratingsQuery.data.value?.items ?? []).filter((e) => e.rating !== null)
  return entriesToGridProps(rated)
})

// Favoriler
const favoritesQuery = useQuery(() => ({
  queryKey: ['profile-favorites', props.username],
  queryFn: () => getUserLibraryRequest(props.username, { favorite: true, page_size: 60 }),
}))
const favoritesGrid = computed(() => entriesToGridProps(favoritesQuery.data.value?.items ?? []))

// İncelemeler
const reviews = useUserReviews(() => props.username)
const reviewItems = computed(() => reviews.data.value?.pages.flatMap((p) => p.items) ?? [])

// Listeler
const listsQuery = useQuery(() => ({
  queryKey: ['profile-lists', props.username],
  queryFn: () => getUserListsRequest(props.username),
}))

// Takip et/bırak
const followMutation = useFollowUser()
const unfollowMutation = useUnfollowUser()
const followPending = ref(false)

async function toggleFollow() {
  if (!profile.data.value) return
  if (!auth.isAuthenticated) {
    toast.info('Bunun için giriş yapmalısın')
    void router.push({ path: '/giris', query: { redirect: route.fullPath } })
    return
  }
  followPending.value = true
  try {
    if (profile.data.value.is_following) await unfollowMutation.mutateAsync(props.username)
    else await followMutation.mutateAsync(props.username)
    await profile.refetch()
  } catch {
    toast.error('Bir şeyler ters gitti')
  } finally {
    followPending.value = false
  }
}

const editModalOpen = ref(false)
const newListModalOpen = ref(false)
const followListModalOpen = ref(false)
const followListMode = ref<'followers' | 'following'>('followers')

function showFollowers() {
  followListMode.value = 'followers'
  followListModalOpen.value = true
}
function showFollowing() {
  followListMode.value = 'following'
  followListModalOpen.value = true
}
</script>

<template>
  <div v-if="profile.isPending.value" class="flex flex-col gap-4 py-6">
    <BaseSkeleton class="h-32 w-full" rounded="lg" />
  </div>

  <EmptyState v-else-if="is404" title="Böyle bir kullanıcı yok" />

  <ErrorState v-else-if="profile.isError.value" message="Profil yüklenemedi." @retry="() => profile.refetch()" />

  <div v-else-if="profile.data.value" class="flex flex-col gap-6 py-6">
    <ProfileHeader
      :profile="profile.data.value"
      :summary="summary.data.value"
      :follow-pending="followPending"
      @edit-profile="editModalOpen = true"
      @new-list="newListModalOpen = true"
      @show-followers="showFollowers"
      @show-following="showFollowing"
      @toggle-follow="toggleFollow"
    />

    <BaseTabs v-model="tab" :tabs="TABS" />

    <template v-if="tab === 'aktiviteler'">
      <div v-if="activities.isPending.value" class="flex flex-col gap-4">
        <BaseSkeleton v-for="i in 3" :key="i" class="h-40 w-full" rounded="lg" />
      </div>
      <EmptyState v-else-if="activityItems.length === 0" title="Henüz aktivite yok" />
      <div v-else class="flex flex-col gap-4">
        <ActivityCard v-for="activity in activityItems" :key="activity.id" :activity="activity" />
        <BaseButton v-if="activities.hasNextPage.value" variant="secondary" :loading="activities.isFetchingNextPage.value" @click="activities.fetchNextPage()">
          Daha fazla yükle
        </BaseButton>
      </div>
    </template>

    <template v-else-if="tab === 'kutuphane'">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="filter in LIBRARY_FILTERS"
            :key="filter.key"
            type="button"
            class="rounded-full border px-3 py-1.5 text-sm"
            :class="librarySubTab === filter.key ? 'border-brand-500 bg-brand-500/15 text-link' : 'border-border text-fg hover:bg-surface-2'"
            @click="librarySubTab = filter.key"
          >
            {{ filter.label }}
          </button>
        </div>
        <BaseSelect
          v-model="librarySort"
          aria-label="Kütüphaneyi sırala"
          :options="[
            { value: 'recent', label: 'Son eklenen' },
            { value: 'rating', label: 'Puan' },
            { value: 'title', label: 'Başlık' },
            { value: 'year', label: 'Yıl' },
          ]"
        />
      </div>
      <ContentGrid :items="libraryGrid.items" :lookup="libraryGrid.lookup" :loading="libraryIsPending" empty-title="Bu sekmede içerik yok" />
    </template>

    <template v-else-if="tab === 'puanlar'">
      <ContentGrid :items="ratingsGrid.items" :lookup="ratingsGrid.lookup" :loading="ratingsQuery.isPending.value" empty-title="Henüz puanlama yok" />
    </template>

    <template v-else-if="tab === 'incelemeler'">
      <div v-if="reviews.isPending.value" class="flex justify-center py-6"><BaseSpinner /></div>
      <EmptyState v-else-if="reviewItems.length === 0" title="Henüz inceleme yok" />
      <div v-else class="flex flex-col gap-3">
        <ReviewItem v-for="review in reviewItems" :key="review.id" :review="review" />
        <BaseButton v-if="reviews.hasNextPage.value" variant="secondary" :loading="reviews.isFetchingNextPage.value" @click="reviews.fetchNextPage()">
          Daha fazla
        </BaseButton>
      </div>
    </template>

    <template v-else-if="tab === 'listeler'">
      <div v-if="listsQuery.isPending.value" class="flex justify-center py-6"><BaseSpinner /></div>
      <EmptyState v-else-if="(listsQuery.data.value?.items.length ?? 0) === 0" title="Henüz liste yok" />
      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <ListCard v-for="list in listsQuery.data.value?.items" :key="list.id" :list="list" />
      </div>
    </template>

    <template v-else-if="tab === 'favoriler'">
      <ContentGrid :items="favoritesGrid.items" :lookup="favoritesGrid.lookup" :loading="favoritesQuery.isPending.value" empty-title="Henüz favori yok" />
    </template>

    <template v-else-if="tab === 'istatistik'">
      <div class="flex flex-col gap-4">
        <div class="flex items-center justify-between gap-3">
          <RouterLink v-if="profile.data.value?.is_me" :to="`/ozet/${statsYear}`" class="text-sm font-medium text-link hover:underline">
            {{ statsYear }} Yıllık Özetini gör →
          </RouterLink>
          <span v-else />
          <BaseSelect v-model="statsYear" aria-label="Yıl seç" :options="YEAR_OPTIONS" />
        </div>
        <div v-if="stats.isPending.value" class="flex justify-center py-6"><BaseSpinner /></div>
        <ErrorState v-else-if="stats.isError.value" message="İstatistikler yüklenemedi." @retry="() => stats.refetch()" />
        <StatsCharts v-else-if="stats.data.value" :stats="stats.data.value" />
      </div>
    </template>

    <EditProfileModal v-model="editModalOpen" />
    <ListFormModal v-model="newListModalOpen" />
    <UserListModal v-model="followListModalOpen" :username="username" :mode="followListMode" />
  </div>
</template>
