<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { X } from 'lucide-vue-next'
import { useWrapped } from '@/api/stats'
import { contentPath } from '@/utils/content'
import { formatPages, formatRuntime } from '@/utils/format'
import BaseSpinner from '@/components/ui/BaseSpinner.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import SafeImage from '@/components/ui/SafeImage.vue'

const route = useRoute()
const router = useRouter()

const year = computed(() => (route.params.year ? Number(route.params.year) : new Date().getFullYear()))
const wrapped = useWrapped(year)

const MONTH_NAMES = [
  'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
  'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık',
]

const topPeople = computed(() => wrapped.data.value?.stats.top_people ?? [])
const highestRated = computed(() => wrapped.data.value?.stats.highlights?.highest_rated ?? [])

const slides = computed<string[]>(() => {
  const w = wrapped.data.value
  if (!w) return []
  const list = ['intro', 'totals', 'time']
  if (w.dominant_genre) list.push('genre')
  if (topPeople.value.length > 0) list.push('people')
  if (w.most_active_month) list.push('month')
  if (w.first_completed) list.push('first-last')
  if (w.most_liked_review || highestRated.value.length > 0) list.push('highlight')
  list.push('outro')
  return list
})

const current = ref(0)

function next() {
  if (current.value < slides.value.length - 1) current.value++
  else close()
}
function prev() {
  if (current.value > 0) current.value--
}
function close() {
  void router.push('/kesfet')
}
function onTapZone(event: MouseEvent) {
  if (event.clientX < window.innerWidth / 3) prev()
  else next()
}
function onKeydown(event: KeyboardEvent) {
  if (event.key === 'ArrowRight' || event.key === ' ') next()
  else if (event.key === 'ArrowLeft') prev()
  else if (event.key === 'Escape') close()
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <div class="fixed inset-0 z-50 flex flex-col bg-bg">
    <div v-if="slides.length > 0" class="flex gap-1 p-3 pt-[max(0.75rem,env(safe-area-inset-top))]">
      <div v-for="(slideId, i) in slides" :key="slideId" class="h-1 flex-1 overflow-hidden rounded-full bg-surface-2">
        <div class="h-full bg-brand-600 motion-safe:transition-all motion-safe:duration-300" :class="i <= current ? 'w-full' : 'w-0'" />
      </div>
    </div>

    <button
      type="button"
      aria-label="Kapat"
      class="absolute top-4 right-4 z-10 flex size-9 items-center justify-center rounded-full text-muted hover:bg-surface-2 hover:text-fg"
      @click="close"
    >
      <X class="size-5" />
    </button>

    <div v-if="wrapped.isPending.value" class="flex flex-1 items-center justify-center"><BaseSpinner /></div>
    <ErrorState
      v-else-if="wrapped.isError.value"
      message="Yıllık özet yüklenemedi."
      class="m-auto"
      @retry="() => wrapped.refetch()"
    />

    <div v-else-if="wrapped.data.value" class="relative flex flex-1 touch-manipulation select-none" @click="onTapZone">
      <Transition
        mode="out-in"
        enter-active-class="motion-safe:transition-opacity motion-safe:duration-300"
        enter-from-class="opacity-0"
        leave-active-class="motion-safe:transition-opacity motion-safe:duration-150"
        leave-to-class="opacity-0"
      >
        <div :key="slides[current]" class="flex flex-1 flex-col items-center justify-center gap-4 p-8 text-center">
          <template v-if="slides[current] === 'intro'">
            <p class="text-sm font-medium text-muted">{{ year }} Yılın Özeti</p>
            <h1 class="text-4xl font-bold text-fg">Senin {{ year }}'in! 🎬📚</h1>
            <p class="text-muted">Bu yıl neler izlediğine, okuduğuna bir bakalım…</p>
          </template>

          <template v-else-if="slides[current] === 'totals'">
            <p class="text-sm font-medium text-muted">Bu yıl tamamladıkların</p>
            <div class="flex gap-6">
              <div>
                <p class="text-4xl font-bold text-fg">{{ wrapped.data.value.stats.totals.movies }}</p>
                <p class="text-sm text-muted">film</p>
              </div>
              <div>
                <p class="text-4xl font-bold text-fg">{{ wrapped.data.value.stats.totals.tv }}</p>
                <p class="text-sm text-muted">dizi</p>
              </div>
              <div>
                <p class="text-4xl font-bold text-fg">{{ wrapped.data.value.stats.totals.books }}</p>
                <p class="text-sm text-muted">kitap</p>
              </div>
            </div>
          </template>

          <template v-else-if="slides[current] === 'time'">
            <p class="text-sm font-medium text-muted">Harcadığın zaman</p>
            <p class="text-3xl font-bold text-fg">{{ formatRuntime(wrapped.data.value.stats.totals.minutes) }}</p>
            <p class="text-muted">film izledin</p>
            <p class="mt-4 text-3xl font-bold text-fg">{{ formatPages(wrapped.data.value.stats.totals.pages) }}</p>
            <p class="text-muted">okudun</p>
          </template>

          <template v-else-if="slides[current] === 'genre'">
            <p class="text-sm font-medium text-muted">Bu yılki türün</p>
            <h2 class="text-3xl font-bold text-fg">{{ wrapped.data.value.dominant_genre?.label }}</h2>
            <p class="text-muted">Bu yıl sen bir…</p>
            <p class="text-2xl font-bold text-link">{{ wrapped.data.value.fun_title }}</p>
          </template>

          <template v-else-if="slides[current] === 'people'">
            <p class="text-sm font-medium text-muted">Bu yıl en çok takip ettiğin isim</p>
            <h2 class="text-3xl font-bold text-fg">{{ topPeople[0]?.name }}</h2>
            <p class="text-muted">{{ topPeople[0]?.count }} içerikte karşına çıktı</p>
          </template>

          <template v-else-if="slides[current] === 'month'">
            <p class="text-sm font-medium text-muted">En aktif olduğun ay</p>
            <h2 class="text-3xl font-bold text-fg">{{ MONTH_NAMES[(wrapped.data.value.most_active_month ?? 1) - 1] }}</h2>
          </template>

          <template v-else-if="slides[current] === 'first-last'">
            <div class="flex flex-col gap-6 sm:flex-row">
              <div v-if="wrapped.data.value.first_completed" class="flex flex-col items-center gap-2">
                <p class="text-sm font-medium text-muted">Yılın ilki</p>
                <SafeImage
                  :src="wrapped.data.value.first_completed.poster_url"
                  :alt="wrapped.data.value.first_completed.title"
                  class="aspect-[2/3] w-28 rounded-card object-cover"
                />
                <p class="max-w-32 text-sm font-medium text-fg">{{ wrapped.data.value.first_completed.title }}</p>
              </div>
              <div v-if="wrapped.data.value.last_completed" class="flex flex-col items-center gap-2">
                <p class="text-sm font-medium text-muted">Yılın sonuncusu</p>
                <SafeImage
                  :src="wrapped.data.value.last_completed.poster_url"
                  :alt="wrapped.data.value.last_completed.title"
                  class="aspect-[2/3] w-28 rounded-card object-cover"
                />
                <p class="max-w-32 text-sm font-medium text-fg">{{ wrapped.data.value.last_completed.title }}</p>
              </div>
            </div>
          </template>

          <template v-else-if="slides[current] === 'highlight'">
            <template v-if="wrapped.data.value.most_liked_review">
              <p class="text-sm font-medium text-muted">En beğenilen incelemen</p>
              <p class="max-w-md text-fg italic">"{{ wrapped.data.value.most_liked_review.excerpt }}"</p>
              <p class="text-sm text-muted">{{ wrapped.data.value.most_liked_review.content.title }} · {{ wrapped.data.value.most_liked_review.likes_count }} beğeni</p>
            </template>
            <template v-else-if="highestRated[0]">
              <p class="text-sm font-medium text-muted">Yılın en yüksek puanlısı</p>
              <SafeImage :src="highestRated[0].poster_url" :alt="highestRated[0].title" class="aspect-[2/3] w-32 rounded-card object-cover" />
              <p class="text-lg font-bold text-fg">{{ highestRated[0].title }}</p>
            </template>
          </template>

          <template v-else-if="slides[current] === 'outro'">
            <h1 class="text-3xl font-bold text-fg">İşte {{ year }} özetin! 🎉</h1>
            <p class="text-muted">Paylaşmak için ekran görüntüsü alıp arkadaşlarınla paylaşabilirsin.</p>
            <RouterLink
              v-if="highestRated[0]"
              :to="contentPath(highestRated[0].type, highestRated[0].external_id)"
              class="mt-2 text-sm font-medium text-link hover:underline"
              @click.stop
            >
              Yılın favorine göz at
            </RouterLink>
          </template>
        </div>
      </Transition>
    </div>
  </div>
</template>
