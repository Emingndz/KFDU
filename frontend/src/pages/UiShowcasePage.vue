<script setup lang="ts">
import { ref } from 'vue'
import { toast } from 'vue-sonner'
import { Heart, Settings } from 'lucide-vue-next'

import { useTheme } from '@/composables/useTheme'
import { useConfirm } from '@/composables/useConfirm'

import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseTextarea from '@/components/ui/BaseTextarea.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseTabs from '@/components/ui/BaseTabs.vue'
import BaseAvatar from '@/components/ui/BaseAvatar.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import BaseSpinner from '@/components/ui/BaseSpinner.vue'

import StarRating from '@/components/content/StarRating.vue'
import RatingDisplay from '@/components/content/RatingDisplay.vue'
import RatingHistogram from '@/components/content/RatingHistogram.vue'
import GenreChips from '@/components/content/GenreChips.vue'
import PosterCard from '@/components/content/PosterCard.vue'
import ContentGrid from '@/components/content/ContentGrid.vue'
import ContentRow from '@/components/content/ContentRow.vue'
import LibraryButtons from '@/components/content/LibraryButtons.vue'
import FavoriteButton from '@/components/content/FavoriteButton.vue'
import AddToListMenu from '@/components/content/AddToListMenu.vue'
import LikeButton from '@/components/content/LikeButton.vue'
import ActivityCard from '@/components/content/ActivityCard.vue'
import type { ActivityOut, ContentSummary, LibraryStatus } from '@/types'

const { mode, options: themeOptions } = useTheme()
const { confirm } = useConfirm()

const textValue = ref('')
const textareaValue = ref('')
const selectValue = ref('')
const modalOpen = ref(false)
const activeTab = ref('genel')
const loadingDemo = ref(false)

const demoContent: ContentSummary[] = [
  {
    id: 1,
    type: 'movie',
    source: 'tmdb',
    external_id: '27205',
    title: 'Inception',
    original_title: null,
    year: 2010,
    poster_url: null,
    genres: ['science_fiction', 'action'],
    external_rating: 8.4,
    creators: ['Christopher Nolan'],
  },
  {
    id: 2,
    type: 'book',
    source: 'openlibrary',
    external_id: 'OL45804W',
    title: 'Sefiller',
    original_title: null,
    year: 1862,
    poster_url: null,
    genres: ['classics', 'historical_fiction'],
    external_rating: 9.1,
    creators: ['Victor Hugo'],
  },
  {
    id: 3,
    type: 'tv',
    source: 'tmdb',
    external_id: '1396',
    title: 'Breaking Bad',
    original_title: null,
    year: 2008,
    poster_url: null,
    genres: ['drama', 'crime'],
    external_rating: 8.9,
    creators: [],
  },
]

const demoActor = { id: 1, username: 'ada', display_name: 'Ada Lovelace', avatar_url: null, bio: null }
const demoActivities: ActivityOut[] = [
  {
    id: 1,
    card_type: 'rating',
    actor: demoActor,
    content: demoContent[0]!,
    rating: 8,
    review: null,
    status: null,
    list: null,
    created_at: new Date().toISOString(),
    likes_count: 3,
    liked_by_me: false,
    comments_count: 0,
    comments_preview: [],
  },
  {
    id: 2,
    card_type: 'review',
    actor: demoActor,
    content: demoContent[1]!,
    rating: 9,
    review: { id: 1, excerpt: 'Bu kitap gerçekten çok etkileyiciydi, herkese tavsiye ederim…', is_truncated: true, has_spoiler: false },
    status: null,
    list: null,
    created_at: new Date().toISOString(),
    likes_count: 1,
    liked_by_me: true,
    comments_count: 2,
    comments_preview: [],
  },
  {
    id: 3,
    card_type: 'status',
    actor: demoActor,
    content: demoContent[2]!,
    rating: null,
    review: null,
    status: 'in_progress',
    list: null,
    created_at: new Date().toISOString(),
    likes_count: 0,
    liked_by_me: false,
    comments_count: 0,
    comments_preview: [],
  },
  {
    id: 4,
    card_type: 'list_add',
    actor: demoActor,
    content: demoContent[0]!,
    rating: null,
    review: null,
    status: null,
    list: { id: 1, title: 'Favori Bilim Kurgu', item_count: 5, cover_urls: [] },
    created_at: new Date().toISOString(),
    likes_count: 0,
    liked_by_me: false,
    comments_count: 0,
    comments_preview: [],
  },
  {
    id: 5,
    card_type: 'list_create',
    actor: demoActor,
    content: null,
    rating: null,
    review: null,
    status: null,
    list: { id: 2, title: 'Yaz Tatili Listesi', item_count: 4, cover_urls: [] },
    created_at: new Date().toISOString(),
    likes_count: 0,
    liked_by_me: false,
    comments_count: 0,
    comments_preview: [],
  },
]

const demoRating = ref<number | null>(7)
const demoStatus = ref<LibraryStatus | null>('in_progress')
const demoFavorite = ref(false)
const demoLiked = ref(false)
const demoLikes = ref(12)


async function onConfirmDemo() {
  const ok = await confirm({
    title: 'Emin misin?',
    message: 'Bu işlem geri alınamaz.',
    confirmText: 'Evet, sil',
    danger: true,
  })
  toast[ok ? 'success' : 'info'](ok ? 'Onaylandı' : 'Vazgeçildi')
}

function toggleLoadingDemo() {
  loadingDemo.value = true
  setTimeout(() => (loadingDemo.value = false), 1500)
}
</script>

<template>
  <div class="mx-auto max-w-4xl space-y-10 p-8">
    <header class="flex items-center justify-between">
      <h1 class="text-3xl font-bold">KFDU — Bileşen Vitrini</h1>
      <BaseSelect v-model="mode" :options="themeOptions.map((o) => ({ value: o.value, label: o.label }))" />
    </header>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Butonlar</h2>
      <div class="flex flex-wrap items-center gap-3">
        <BaseButton variant="primary">Birincil</BaseButton>
        <BaseButton variant="secondary">İkincil</BaseButton>
        <BaseButton variant="ghost">Hayalet</BaseButton>
        <BaseButton variant="danger">Tehlike</BaseButton>
        <BaseButton variant="link">Bağlantı</BaseButton>
        <BaseButton :loading="loadingDemo" @click="toggleLoadingDemo">Yükleniyor demo</BaseButton>
        <BaseButton disabled>Devre dışı</BaseButton>
        <BaseButton size="sm">Küçük</BaseButton>
        <BaseButton size="lg">Büyük</BaseButton>
        <BaseButton>
          <template #icon><Heart class="size-4" /></template>
          İkonlu
        </BaseButton>
      </div>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Form elemanları</h2>
      <div class="grid gap-4 sm:grid-cols-2">
        <BaseInput v-model="textValue" label="Kullanıcı adı" hint="3-30 karakter" :maxlength="30" />
        <BaseInput label="Şifre" type="password" placeholder="••••••••" />
        <BaseInput label="Hatalı alan" error="Bu alan zorunlu" />
        <BaseSelect
          v-model="selectValue"
          label="Tür"
          placeholder="Seç"
          :options="[
            { value: 'action', label: 'Aksiyon' },
            { value: 'drama', label: 'Dram' },
          ]"
        />
        <BaseTextarea
          v-model="textareaValue"
          label="İnceleme"
          hint="En az 3 karakter"
          :maxlength="500"
          class="sm:col-span-2"
        />
      </div>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Rozet, iskelet, avatar</h2>
      <div class="flex flex-wrap items-center gap-3">
        <BaseBadge variant="movie">Film</BaseBadge>
        <BaseBadge variant="tv">Dizi</BaseBadge>
        <BaseBadge variant="book">Kitap</BaseBadge>
        <BaseBadge variant="success">★ 8.4</BaseBadge>
        <BaseBadge variant="danger">Hata</BaseBadge>
        <BaseAvatar name="Ada Lovelace" size="sm" />
        <BaseAvatar name="Kerem Yılmaz" size="md" />
        <BaseAvatar name="Zeynep Öz" size="lg" src="/broken-image.jpg" />
        <BaseSpinner />
      </div>
      <div class="flex gap-3">
        <BaseSkeleton class="h-24 w-16" rounded="lg" />
        <BaseSkeleton class="h-4 w-40" />
        <BaseSkeleton class="size-10" rounded="full" />
      </div>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Sekmeler</h2>
      <BaseTabs
        v-model="activeTab"
        :tabs="[
          { value: 'genel', label: 'Genel' },
          { value: 'kutuphane', label: 'Kütüphane' },
          { value: 'listeler', label: 'Listeler' },
        ]"
      />
      <p class="text-sm text-muted">Aktif sekme: {{ activeTab }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Modal ve onay</h2>
      <div class="flex gap-3">
        <BaseButton @click="modalOpen = true">Modal aç</BaseButton>
        <BaseButton variant="danger" @click="onConfirmDemo">
          <template #icon><Settings class="size-4" /></template>
          Onay iste
        </BaseButton>
      </div>
      <BaseModal v-model="modalOpen" title="Örnek modal">
        <p class="text-sm text-muted">Esc ile veya dışarı tıklayarak kapatabilirsin.</p>
        <template #footer>
          <BaseButton variant="secondary" @click="modalOpen = false">Kapat</BaseButton>
        </template>
      </BaseModal>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Durum bileşenleri</h2>
      <div class="rounded-card border border-border">
        <EmptyState title="Henüz hiçbir şey yok" message="Buraya içerik eklendiğinde görünecek." />
      </div>
      <div class="rounded-card border border-border">
        <ErrorState message="Sunucuya ulaşılamadı." @retry="toast.info('Tekrar deneniyor…')" />
      </div>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Puanlama</h2>
      <div class="flex flex-wrap items-center gap-6">
        <div class="flex flex-col gap-1">
          <StarRating v-model="demoRating" />
          <p class="text-xs text-muted">Seçilen: {{ demoRating ?? '—' }}/10</p>
        </div>
        <RatingDisplay :rating="8" />
        <StarRating :model-value="6" readonly size="sm" />
      </div>
      <RatingHistogram :distribution="{ '1': 1, '2': 0, '3': 2, '4': 1, '5': 3, '6': 5, '7': 9, '8': 14, '9': 7, '10': 4 }" />
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Tür etiketleri</h2>
      <GenreChips :genres="['Bilim Kurgu', 'Aksiyon', 'Gerilim']" />
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">İçerik kartları</h2>
      <div class="flex gap-4">
        <PosterCard v-for="item in demoContent" :key="`${item.type}:${item.external_id}`" :content="item" />
      </div>
      <ContentRow title="Örnek şerit" :items="demoContent" />
      <ContentGrid :items="demoContent" />
      <ContentGrid :items="[]" loading :skeleton-count="6" />
      <ContentGrid :items="[]" empty-title="Sonuç yok" empty-message="Filtreleri değiştirip tekrar dene." />
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Kütüphane eylemleri</h2>
      <div class="flex flex-wrap items-center gap-3">
        <LibraryButtons type="movie" :status="demoStatus" @update:status="(v) => (demoStatus = demoStatus === v ? null : v)" />
        <FavoriteButton v-model="demoFavorite" />
        <AddToListMenu type="movie" external-id="27205" :content-id="1" />
        <LikeButton
          :model-value="demoLiked"
          :count="demoLikes"
          @update:model-value="
            (v) => {
              demoLiked = v
              demoLikes += v ? 1 : -1
            }
          "
        />
      </div>
      <p class="text-xs text-muted">Durum: {{ demoStatus ?? '—' }} · Favori: {{ demoFavorite }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Akış kartları</h2>
      <p class="text-xs text-muted">
        Sahte verilerle gösteriliyor — beğeni/yorum tıklamaları gerçek olmayan bir aktivite kimliğine gittiği için hata
        toast'u gösterebilir, bu beklenen bir durumdur.
      </p>
      <div class="flex flex-col gap-4">
        <ActivityCard v-for="activity in demoActivities" :key="activity.id" :activity="activity" />
      </div>
    </section>
  </div>
</template>
