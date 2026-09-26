<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, type RouteLocationRaw } from 'vue-router'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import type { ContentSummary } from '@/types'
import PosterCard from './PosterCard.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'

withDefaults(
  defineProps<{
    title: string
    items: ContentSummary[]
    loading?: boolean
    seeAllTo?: RouteLocationRaw
  }>(),
  { loading: false },
)

const scrollerRef = ref<HTMLElement | null>(null)

function scrollBy(direction: 1 | -1) {
  scrollerRef.value?.scrollBy({ left: direction * 480, behavior: 'smooth' })
}
</script>

<template>
  <section class="flex flex-col gap-3">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-fg">{{ title }}</h2>
      <RouterLink v-if="seeAllTo" :to="seeAllTo" class="text-sm text-brand-600 hover:underline">Tümü</RouterLink>
    </div>

    <div class="relative">
      <button
        type="button"
        aria-label="Geri kaydır"
        class="absolute top-1/2 left-0 z-10 hidden size-9 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-border bg-surface shadow-md sm:flex"
        @click="scrollBy(-1)"
      >
        <ChevronLeft class="size-4" />
      </button>

      <div ref="scrollerRef" class="flex gap-4 overflow-x-auto scroll-smooth pb-2">
        <template v-if="loading">
          <div v-for="i in 8" :key="i" class="flex w-36 shrink-0 flex-col gap-1.5">
            <BaseSkeleton class="aspect-[2/3] w-full" rounded="lg" />
            <BaseSkeleton class="h-4 w-3/4" />
          </div>
        </template>
        <template v-else>
          <PosterCard
            v-for="item in items"
            :key="`${item.type}:${item.external_id}`"
            :content="item"
            class="shrink-0"
          />
        </template>
      </div>

      <button
        type="button"
        aria-label="İleri kaydır"
        class="absolute top-1/2 right-0 z-10 hidden size-9 translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-border bg-surface shadow-md sm:flex"
        @click="scrollBy(1)"
      >
        <ChevronRight class="size-4" />
      </button>
    </div>
  </section>
</template>
