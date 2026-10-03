<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { StorageSerializers, useLocalStorage } from '@vueuse/core'
import { toast } from 'vue-sonner'
import { CircleAlert, CircleCheck, FileUp } from 'lucide-vue-next'
import { ApiError } from '@/api/client'
import { isImportActive, useImportJob, useRefreshAfterImport, useStartImport } from '@/api/transfer'
import { useAuthStore } from '@/stores/auth'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseSpinner from '@/components/ui/BaseSpinner.vue'
import type { ImportFileKind, ImportJobOut, ImportSource } from '@/types'

const props = defineProps<{ source: ImportSource }>()

const MAX_FILE_BYTES = 5 * 1024 * 1024
const UNMATCHED_PREVIEW = 50

const COPY: Record<ImportSource, { title: string; description: string; steps: string[]; dotClass: string }> = {
  letterboxd: {
    title: 'Letterboxd',
    description: 'İzlediğin filmleri, puanlarını, incelemelerini ve izleme listeni getir.',
    steps: [
      'letterboxd.com’da Settings → Import & Export sekmesinden “Export your data” de.',
      'İnen ZIP dosyasını açmadan olduğu gibi buraya yükle; izlediklerin, puanların, incelemelerin ve izleme listen tek seferde gelir.',
      'İstersen ZIP’in içindeki ratings.csv, watched.csv, watchlist.csv, diary.csv ya da reviews.csv dosyalarını da tek tek yükleyebilirsin.',
    ],
    dotClass: 'bg-movie',
  },
  goodreads: {
    title: 'Goodreads',
    description: 'Okuduğun, okumakta olduğun ve okumak istediğin kitapları puanlarıyla getir.',
    steps: [
      'goodreads.com’da My Books → Import and export sayfasına gir.',
      '“Export Library” de; dosya hazır olunca çıkan bağlantıdan indir.',
      'goodreads_library_export.csv dosyasını buraya yükle.',
    ],
    dotClass: 'bg-book',
  },
}

const FILE_KIND_LABELS: Record<ImportFileKind, string> = {
  ratings: 'ratings.csv — puanlarınla birlikte “İzledim” olarak',
  diary: 'diary.csv — izleme tarihleri ve puanlarınla',
  reviews: 'reviews.csv — puanların ve inceleme metinlerinle',
  archive: 'Letterboxd arşivi — izlediklerin, puanların, incelemelerin ve izleme listen',
  watched: 'watched.csv — “İzledim” olarak',
  watchlist: 'watchlist.csv — “İzleyeceğim” olarak',
  goodreads_library: 'Goodreads rafları — Okudum / Okuyorum / Okuyacağım',
}

const copy = computed(() => COPY[props.source])
// Yalnız Letterboxd'un dışa aktarımı ZIP olarak gelir; Goodreads tek bir CSV verir
const acceptsZip = computed(() => props.source === 'letterboxd')
const auth = useAuthStore()

// İş kimliği tarayıcıda saklanır: sayfadan ayrılıp dönünce ilerleme ya da sonuç kaldığı yerden görünür
const jobId = useLocalStorage<number | null>(`kfdu:import-job:${props.source}`, null, {
  serializer: StorageSerializers.object,
})
const jobQuery = useImportJob(jobId)
const job = computed(() => jobQuery.data.value)
const startImport = useStartImport()
const refreshAfterImport = useRefreshAfterImport()
const fileInput = ref<HTMLInputElement | null>(null)

// Başka hesaba ait ya da silinmiş eski iş: sessizce unut
watch(
  () => jobQuery.error.value,
  (error) => {
    if (error instanceof ApiError && error.status === 404) jobId.value = null
  },
)

// Bu görünümde başlatılan ya da sürerken görülen iş bitince veriler tazelenir ve haber verilir
const awaitingResult = ref(false)
const etaText = ref<string | null>(null)
let progressSample: { at: number; processed: number } | null = null

function updateEta(current: ImportJobOut) {
  if (progressSample === null) {
    progressSample = { at: Date.now(), processed: current.processed }
    return
  }
  const rowsDone = current.processed - progressSample.processed
  if (rowsDone <= 0) return
  // Hız istemcide ölçülür: sunucu saatiyle tarayıcı saati arasındaki farktan etkilenmez
  const msPerRow = (Date.now() - progressSample.at) / rowsDone
  const minutes = Math.ceil(((current.total - current.processed) * msPerRow) / 60_000)
  etaText.value = minutes <= 1 ? 'bir dakikadan az kaldı' : `yaklaşık ${minutes} dk kaldı`
}

watch(job, (current) => {
  if (!current) return
  if (isImportActive(current)) {
    awaitingResult.value = true
    updateEta(current)
    return
  }
  progressSample = null
  etaText.value = null
  if (!awaitingResult.value) return
  awaitingResult.value = false
  void refreshAfterImport()
  if (current.status === 'done') toast.success(`İçe aktarma tamamlandı: ${current.matched}/${current.total} eşleşti`)
  else toast.error('İçe aktarma tamamlanamadı')
})

const percent = computed(() => (job.value && job.value.total ? Math.round((job.value.processed / job.value.total) * 100) : 0))
const fileKindLabel = computed(() => {
  const kind = job.value?.report.file_kind
  return kind ? FILE_KIND_LABELS[kind] : null
})
const unmatched = computed(() => job.value?.report.unmatched ?? [])
const hiddenUnmatched = computed(() => Math.max(0, unmatched.value.length - UNMATCHED_PREVIEW))
// Kütüphanenin içe aktarılan içeriği gösteren rafına iner (varsayılan raf filmler olduğundan kitapta boş görünürdü)
const libraryLink = computed(() => {
  let shelf = 'okunan'
  if (props.source === 'letterboxd') shelf = job.value?.report.file_kind === 'watchlist' ? 'izlenecek' : 'izlenen'
  return { path: `/u/${auth.me?.username ?? ''}`, query: { sekme: 'kutuphane', raf: shelf } }
})

function chooseFile() {
  fileInput.value?.click()
}

async function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = '' // aynı dosya yeniden seçilebilsin
  if (!file) return
  if (!acceptsZip.value && /\.zip$/i.test(file.name)) {
    toast.error('ZIP dosyasını açıp içindeki CSV dosyasını seç')
    return
  }
  if (!(acceptsZip.value ? /\.(csv|zip)$/i : /\.csv$/i).test(file.name)) {
    toast.error(acceptsZip.value ? 'Dışa aktarılan .zip ya da .csv dosyasını seç' : 'Dışa aktarılan .csv dosyasını seç')
    return
  }
  if (file.size > MAX_FILE_BYTES) {
    toast.error('Dosya en fazla 5 MB olabilir')
    return
  }
  try {
    const { job_id } = await startImport.mutateAsync({ source: props.source, file })
    awaitingResult.value = true
    jobId.value = job_id
  } catch (error) {
    toast.error(error instanceof ApiError ? error.message : 'Dosya yüklenemedi, tekrar dene')
  }
}

function reset() {
  jobId.value = null
}
</script>

<template>
  <article class="flex flex-col gap-3 rounded-card border border-border bg-surface p-4">
    <header class="flex items-start gap-3">
      <span class="mt-1.5 size-2.5 shrink-0 rounded-full" :class="copy.dotClass" aria-hidden="true" />
      <div>
        <h4 class="font-semibold text-fg">{{ copy.title }}</h4>
        <p class="text-sm text-muted">{{ copy.description }}</p>
      </div>
    </header>

    <div v-if="job && isImportActive(job)" class="flex flex-col gap-2">
      <p class="text-sm text-fg" aria-live="polite">
        {{ job.status === 'pending' ? 'Sıraya alındı…' : 'Eşleştiriliyor…' }}
        <span class="text-muted">{{ job.processed }} / {{ job.total }}</span>
      </p>
      <div
        class="h-2 overflow-hidden rounded-full bg-surface-2"
        role="progressbar"
        :aria-valuemin="0"
        :aria-valuemax="job.total"
        :aria-valuenow="job.processed"
        :aria-label="`${copy.title} içe aktarma ilerlemesi`"
      >
        <div class="h-full rounded-full bg-brand-500 transition-[width] motion-safe:duration-500" :style="{ width: `${percent}%` }" />
      </div>
      <p class="text-xs text-muted">
        <template v-if="fileKindLabel">{{ fileKindLabel }}</template>
        <template v-if="etaText"> · {{ etaText }}</template>
      </p>
      <p class="text-xs text-muted">Bu sayfadan ayrılabilirsin; içe aktarma arka planda sürer.</p>
    </div>

    <div v-else-if="job && job.status === 'done'" class="flex flex-col gap-3">
      <p class="flex items-start gap-2 text-sm text-fg">
        <CircleCheck class="size-5 shrink-0 text-success" aria-hidden="true" />
        <span>
          <strong>{{ job.matched }} / {{ job.total }}</strong> içerik eşleşti ve kütüphanene işlendi.
          <span v-if="fileKindLabel" class="block text-xs text-muted">{{ fileKindLabel }}</span>
        </span>
      </p>
      <details v-if="unmatched.length" class="rounded-lg bg-surface-2 p-3 text-sm">
        <summary class="cursor-pointer font-medium text-fg">Eşleşmeyenler ({{ unmatched.length }})</summary>
        <ul class="mt-2 max-h-48 list-disc overflow-y-auto pl-5 text-muted">
          <li v-for="(title, index) in unmatched.slice(0, UNMATCHED_PREVIEW)" :key="index">{{ title }}</li>
        </ul>
        <p v-if="hiddenUnmatched" class="mt-1 text-xs text-muted">ve {{ hiddenUnmatched }} tane daha</p>
        <p class="mt-2 text-xs text-muted">Bunları Keşfet’te arayıp kendin ekleyebilirsin.</p>
      </details>
      <div class="flex flex-wrap gap-2">
        <BaseButton size="sm" :to="libraryLink">Kütüphaneme git</BaseButton>
        <BaseButton size="sm" variant="secondary" @click="reset">Başka dosya yükle</BaseButton>
      </div>
    </div>

    <div v-else-if="job && job.status === 'failed'" class="flex flex-col gap-3">
      <p class="flex items-start gap-2 text-sm text-fg">
        <CircleAlert class="size-5 shrink-0 text-danger" aria-hidden="true" />
        <span>{{ job.error ?? 'İçe aktarma tamamlanamadı.' }}</span>
      </p>
      <p v-if="job.processed" class="text-xs text-muted">
        {{ job.processed }} / {{ job.total }} satır işlendi, {{ job.matched }} içerik eklendi.
      </p>
      <div>
        <BaseButton size="sm" variant="secondary" @click="reset">Tamam</BaseButton>
      </div>
    </div>

    <div v-else-if="jobId !== null && jobQuery.isError.value" class="flex flex-col gap-3">
      <p class="text-sm text-muted">İçe aktarma durumu alınamadı.</p>
      <div class="flex flex-wrap gap-2">
        <BaseButton size="sm" variant="secondary" @click="jobQuery.refetch()">Tekrar dene</BaseButton>
        <BaseButton size="sm" variant="ghost" @click="reset">Vazgeç</BaseButton>
      </div>
    </div>

    <p v-else-if="jobId !== null" class="flex items-center gap-2 text-sm text-muted">
      <BaseSpinner size="sm" />
      Durum alınıyor…
    </p>

    <template v-else>
      <details class="text-sm">
        <summary class="cursor-pointer text-link">Dosyamı nasıl indiririm?</summary>
        <ol class="mt-2 list-decimal space-y-1 pl-5 text-muted">
          <li v-for="step in copy.steps" :key="step">{{ step }}</li>
        </ol>
      </details>
      <div>
        <BaseButton size="sm" :loading="startImport.isPending.value" @click="chooseFile">
          <template #icon><FileUp class="size-4" aria-hidden="true" /></template>
          {{ acceptsZip ? 'ZIP ya da CSV dosyası seç' : 'CSV dosyası seç' }}
        </BaseButton>
        <input
          ref="fileInput"
          type="file"
          :accept="acceptsZip ? '.zip,.csv,application/zip,text/csv' : '.csv,text/csv'"
          class="hidden"
          tabindex="-1"
          :aria-label="`${copy.title} ${acceptsZip ? 'ZIP ya da CSV dosyası' : 'CSV dosyası'}`"
          @change="onFileChange"
        />
      </div>
    </template>
  </article>
</template>
