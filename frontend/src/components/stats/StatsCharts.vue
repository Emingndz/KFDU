<script setup lang="ts">
import { computed } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import { ArcElement, BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, Tooltip } from 'chart.js'
import type { UserStatsOut } from '@/types'
import { formatPages, formatRuntime } from '@/utils/format'

ChartJS.register(BarElement, CategoryScale, LinearScale, ArcElement, Tooltip, Legend)

const props = defineProps<{ stats: UserStatsOut }>()

const MONTH_LABELS = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara']
const GENRE_COLORS = ['#6a47ff', '#14b8a6', '#f97316', '#e5484d', '#3b82f6', '#f5b301', '#16a34a', '#9479ff']

const ratingDistribution = computed(() => props.stats.rating_distribution ?? {})
const topGenres = computed(() => props.stats.top_genres ?? [])
const monthly = computed(() => props.stats.monthly ?? [])

const ratingChartData = computed(() => ({
  labels: Array.from({ length: 10 }, (_, i) => String(i + 1)),
  datasets: [
    {
      label: 'Puan sayısı',
      data: Array.from({ length: 10 }, (_, i) => ratingDistribution.value[i + 1] ?? 0),
      backgroundColor: '#6a47ff',
      borderRadius: 4,
    },
  ],
}))

const genreChartData = computed(() => ({
  labels: topGenres.value.map((g) => g.label),
  datasets: [{ data: topGenres.value.map((g) => g.count), backgroundColor: GENRE_COLORS }],
}))

const monthlyChartData = computed(() => ({
  labels: monthly.value.map((m) => MONTH_LABELS[m.month - 1]),
  datasets: [
    { label: 'Film', data: monthly.value.map((m) => m.movies), backgroundColor: '#3b82f6' },
    { label: 'Dizi', data: monthly.value.map((m) => m.tv), backgroundColor: '#14b8a6' },
    { label: 'Kitap', data: monthly.value.map((m) => m.books), backgroundColor: '#f97316' },
  ],
}))

const barOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
}
const stackedOptions = {
  responsive: true,
  scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true, ticks: { stepSize: 1 } } },
}

const hasAnyActivity = computed(() => {
  const t = props.stats.totals
  return t.movies + t.tv + t.books > 0
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div class="rounded-card border border-border p-3 text-center">
        <p class="text-lg font-bold text-fg">{{ formatRuntime(stats.totals.minutes) }}</p>
        <p class="text-xs text-muted">film süresi</p>
      </div>
      <div class="rounded-card border border-border p-3 text-center">
        <p class="text-lg font-bold text-fg">{{ formatPages(stats.totals.pages) }}</p>
        <p class="text-xs text-muted">okundu</p>
      </div>
      <div class="rounded-card border border-border p-3 text-center">
        <p class="text-lg font-bold text-fg">{{ stats.totals.movies + stats.totals.tv + stats.totals.books }}</p>
        <p class="text-xs text-muted">içerik tamamlandı</p>
      </div>
      <div class="rounded-card border border-border p-3 text-center">
        <p class="text-lg font-bold text-fg">{{ stats.totals.avg_rating?.toFixed(1) ?? '—' }}</p>
        <p class="text-xs text-muted">ortalama puan</p>
      </div>
    </div>

    <div v-if="!hasAnyActivity" class="rounded-card border border-border p-6 text-center text-sm text-muted">
      Bu yıl için henüz tamamlanan içerik yok.
    </div>
    <template v-else>
      <div class="rounded-card border border-border p-4">
        <h3 class="mb-3 text-sm font-semibold text-fg">Aylık aktivite</h3>
        <Bar :data="monthlyChartData" :options="stackedOptions" />
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div v-if="Object.keys(ratingDistribution).length > 0" class="rounded-card border border-border p-4">
          <h3 class="mb-3 text-sm font-semibold text-fg">Puan dağılımı</h3>
          <Bar :data="ratingChartData" :options="barOptions" />
        </div>
        <div v-if="topGenres.length > 0" class="rounded-card border border-border p-4">
          <h3 class="mb-3 text-sm font-semibold text-fg">Türler</h3>
          <Doughnut :data="genreChartData" />
        </div>
      </div>
    </template>
  </div>
</template>
