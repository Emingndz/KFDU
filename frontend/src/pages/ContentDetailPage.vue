<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { ApiError } from '@/api/client'
import { type CatalogContentType, useContentDetail, useSimilarContent } from '@/api/catalog'
import { useContentState } from '@/api/library'
import { useAuthStore } from '@/stores/auth'
import { useContentActions } from '@/composables/useContentActions'
import { formatPages, formatRuntime } from '@/utils/format'
import { statusLabel, typeLabel } from '@/utils/content'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import SafeImage from '@/components/ui/SafeImage.vue'
import StarRating from '@/components/content/StarRating.vue'
import RatingHistogram from '@/components/content/RatingHistogram.vue'
import GenreChips from '@/components/content/GenreChips.vue'
import LibraryButtons from '@/components/content/LibraryButtons.vue'
import FavoriteButton from '@/components/content/FavoriteButton.vue'
import AddToListMenu from '@/components/content/AddToListMenu.vue'
import CastRow from '@/components/content/CastRow.vue'
import SeasonRow from '@/components/content/SeasonRow.vue'
import WatchProviders from '@/components/content/WatchProviders.vue'
import ReviewEditor from '@/components/content/ReviewEditor.vue'
import ReviewList from '@/components/content/ReviewList.vue'
import TrailerModal from '@/components/content/TrailerModal.vue'
import ContentRow from '@/components/content/ContentRow.vue'

const props = defineProps<{ type: CatalogContentType; externalId: string }>()

const router = useRouter()
const auth = useAuthStore()

const detail = useContentDetail(
  () => props.type,
  () => props.externalId,
)
const contentState = useContentState(
  () => props.type,
  () => props.externalId,
)
const similar = useSimilarContent(
  () => props.type,
  () => props.externalId,
)

const is404 = computed(() => detail.isError.value && detail.error.value instanceof ApiError && detail.error.value.status === 404)

const actions = useContentActions(
  props.type,
  () => props.externalId,
  () =>
    contentState.data.value?.me?.entry
      ? {
          status: contentState.data.value.me.entry.status,
          rating: contentState.data.value.me.entry.rating,
          is_favorite: contentState.data.value.me.entry.is_favorite,
          progress: contentState.data.value.me.entry.progress,
        }
      : undefined,
)

const overviewExpanded = ref(false)
const trailerOpen = ref(false)

const SOURCE_LABELS: Record<string, string> = { tmdb: 'TMDB', openlibrary: 'Open Library', google_books: 'Google Books' }

const metaLine = computed(() => {
  const d = detail.data.value
  if (!d) return ''
  const parts: string[] = []
  if (props.type === 'book') {
    if (d.page_count) parts.push(formatPages(d.page_count))
  } else if (d.runtime_minutes) {
    parts.push(formatRuntime(d.runtime_minutes))
  }
  const genresDetail = d.genres_detail ?? []
  if (genresDetail.length > 0) parts.push(genresDetail.map((g) => g.label).join(', '))
  if (d.original_language) parts.push(d.original_language.toUpperCase())
  return parts.join(' • ')
})

const creatorLine = computed(() => {
  const d = detail.data.value
  if (!d) return ''
  const people = (props.type === 'book' ? d.authors : d.directors) ?? []
  return people.map((p) => p.name).join(', ')
})

const genreLabels = computed(() => (detail.data.value?.genres_detail ?? []).map((g) => g.label))
const castList = computed(() => detail.data.value?.cast ?? [])
const seasonsList = computed(() => detail.data.value?.seasons_detail ?? [])
const providersOrEmpty = computed(
  () => detail.data.value?.providers ?? { flatrate: [], rent: [], buy: [], link: null },
)

watch(
  () => detail.data.value,
  (d) => {
    if (d) document.title = `${d.title} (${d.year ?? '—'}) · KFDU`
  },
)

async function share() {
  try {
    await navigator.clipboard.writeText(window.location.href)
    toast.success('Bağlantı kopyalandı')
  } catch {
    toast.error('Bağlantı kopyalanamadı')
  }
}

function goToDiscover() {
  void router.push('/kesfet')
}

function onProgressChange(event: Event) {
  const value = (event.target as HTMLInputElement).value
  actions.setProgress(value === '' ? null : Number(value))
}
</script>

<template>
  <div v-if="detail.isPending.value" class="flex flex-col gap-6 py-6">
    <BaseSkeleton class="h-64 w-full" rounded="lg" />
    <BaseSkeleton class="h-8 w-1/2" />
    <BaseSkeleton class="h-4 w-1/3" />
  </div>

  <EmptyState
    v-else-if="is404"
    title="Bu içerik bulunamadı"
    message="Aradığın film, dizi veya kitap kaldırılmış ya da hiç var olmamış olabilir."
  >
    <template #action>
      <BaseButton @click="goToDiscover">Keşfet'e dön</BaseButton>
    </template>
  </EmptyState>

  <ErrorState v-else-if="detail.isError.value" message="İçerik yüklenemedi." @retry="() => detail.refetch()" />

  <div v-else-if="detail.data.value" class="flex flex-col gap-8 pb-24">
    <!-- Hero -->
    <div class="relative -mx-4 overflow-hidden sm:mx-0 sm:rounded-card">
      <div
        v-if="detail.data.value.backdrop_url"
        class="absolute inset-0 bg-cover bg-center opacity-30"
        :style="{ backgroundImage: `url(${detail.data.value.backdrop_url})` }"
      />
      <div class="absolute inset-0 bg-gradient-to-t from-bg via-bg/60 to-transparent" />
      <div class="relative flex flex-col gap-4 p-4 sm:flex-row sm:p-6">
        <SafeImage
          :src="detail.data.value.poster_url"
          :alt="detail.data.value.title"
          class="aspect-[2/3] w-32 shrink-0 rounded-card object-cover shadow-lg sm:w-48"
        />
        <div class="flex flex-1 flex-col gap-2">
          <p class="text-xs font-medium text-muted">{{ typeLabel(type) }}</p>
          <h1 class="text-2xl font-bold text-fg sm:text-3xl">{{ detail.data.value.title }}</h1>
          <p v-if="detail.data.value.original_title && detail.data.value.original_title !== detail.data.value.title" class="text-sm text-muted">
            {{ detail.data.value.original_title }} · {{ detail.data.value.year }}
          </p>
          <p v-else class="text-sm text-muted">{{ detail.data.value.year }}</p>
          <p class="text-sm text-muted">{{ metaLine }}</p>
          <p v-if="creatorLine" class="text-sm text-fg">{{ creatorLine }}</p>
          <span
            v-if="detail.data.value.external_rating"
            class="inline-flex w-fit items-center gap-1 rounded-full bg-surface-2 px-2.5 py-1 text-xs font-medium text-fg"
          >
            {{ SOURCE_LABELS[detail.data.value.source] ?? detail.data.value.source }} {{ detail.data.value.external_rating.toFixed(1) }}/10
          </span>
        </div>
      </div>
    </div>

    <!-- Platform puanı -->
    <section v-if="contentState.data.value" class="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-8">
      <div class="flex items-baseline gap-2">
        <span class="text-4xl font-bold text-fg">{{ contentState.data.value.platform.average?.toFixed(1) ?? '—' }}</span>
        <span class="text-sm text-muted">/10 ({{ contentState.data.value.platform.count }} oy)</span>
      </div>
      <RatingHistogram v-if="contentState.data.value.platform.count > 0" :distribution="contentState.data.value.platform.distribution" class="flex-1" />
    </section>

    <!-- Eylem çubuğu -->
    <section class="flex flex-col gap-3 rounded-card border border-border p-4">
      <p v-if="!auth.isAuthenticated" class="text-sm text-muted">Puanlamak ve listene eklemek için giriş yap.</p>
      <div class="flex flex-wrap items-center gap-3">
        <StarRating :model-value="actions.rating.value" @update:model-value="actions.setRating" />
        <LibraryButtons :type="type" :status="actions.status.value" @update:status="actions.setStatus" />
        <FavoriteButton :model-value="actions.isFavorite.value" @update:model-value="actions.toggleFavorite" />
        <AddToListMenu v-if="detail.data.value.id" :type="type" :external-id="externalId" :content-id="detail.data.value.id" />
        <div v-if="type === 'tv' && actions.status.value === 'in_progress'" class="flex items-center gap-2">
          <label for="progress-input" class="text-sm text-muted">Kaçıncı bölümdesin?</label>
          <input
            id="progress-input"
            type="number"
            min="0"
            :value="actions.progress.value ?? ''"
            class="h-10 w-20 rounded-lg border border-border bg-surface px-3 text-sm text-fg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
            @change="onProgressChange"
          />
        </div>
        <BaseButton variant="ghost" @click="share">Paylaş</BaseButton>
        <BaseButton v-if="detail.data.value.trailer_key" variant="ghost" @click="trailerOpen = true">Fragmanı izle</BaseButton>
      </div>
    </section>

    <!-- Özet -->
    <section v-if="detail.data.value.overview" class="flex flex-col gap-2">
      <h2 class="text-lg font-semibold text-fg">Özet</h2>
      <p class="text-sm text-fg" :class="overviewExpanded ? '' : 'line-clamp-4'">{{ detail.data.value.overview }}</p>
      <button
        v-if="!overviewExpanded"
        type="button"
        class="w-fit text-sm font-medium text-link hover:underline"
        @click="overviewExpanded = true"
      >
        Devamını göster
      </button>
    </section>

    <GenreChips v-if="genreLabels.length > 0" :genres="genreLabels" />

    <section v-if="castList.length > 0" class="flex flex-col gap-3">
      <h2 class="text-lg font-semibold text-fg">Oyuncular</h2>
      <CastRow :people="castList" />
    </section>

    <section v-if="type === 'tv' && seasonsList.length > 0" class="flex flex-col gap-3">
      <h2 class="text-lg font-semibold text-fg">Sezonlar</h2>
      <SeasonRow :seasons="seasonsList" />
    </section>

    <section v-if="type !== 'book'" class="flex flex-col gap-3">
      <h2 class="text-lg font-semibold text-fg">Nerede izlenir? (Türkiye)</h2>
      <WatchProviders :providers="providersOrEmpty" />
    </section>

    <ReviewEditor :type="type" :external-id="externalId" :review-id="contentState.data.value?.me?.review_id ?? null" />
    <ReviewList :type="type" :external-id="externalId" />

    <section v-if="contentState.data.value && contentState.data.value.friends.length > 0" class="flex flex-col gap-3">
      <h2 class="text-lg font-semibold text-fg">Arkadaşların</h2>
      <ul class="flex flex-col gap-2">
        <li v-for="friend in contentState.data.value.friends" :key="friend.user.id" class="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm">
          <span class="text-fg">{{ friend.user.display_name || friend.user.username }}</span>
          <span class="text-muted">
            <template v-if="friend.status">{{ statusLabel(friend.status, type) }}</template>
            <template v-if="friend.rating"> · {{ friend.rating }}/10</template>
          </span>
        </li>
      </ul>
    </section>

    <ContentRow v-if="(similar.data.value ?? []).length > 0" title="Benzer içerikler" :items="similar.data.value ?? []" :loading="similar.isPending.value" />

    <TrailerModal v-if="detail.data.value.trailer_key" v-model="trailerOpen" :trailer-key="detail.data.value.trailer_key" />
  </div>
</template>
