<script setup lang="ts">
import type { ContentSummary, LookupEntryOut } from '@/types'
import { contentKey } from '@/utils/content'
import PosterCard from './PosterCard.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import EmptyState from '@/components/ui/EmptyState.vue'

withDefaults(
  defineProps<{
    items: ContentSummary[]
    lookup?: Record<string, LookupEntryOut>
    loading?: boolean
    skeletonCount?: number
    emptyTitle?: string
    emptyMessage?: string
  }>(),
  { loading: false, skeletonCount: 12, emptyTitle: 'Henüz içerik yok' },
)
</script>

<template>
  <div v-if="loading" class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
    <div v-for="i in skeletonCount" :key="i" class="flex flex-col gap-1.5">
      <BaseSkeleton class="aspect-[2/3] w-full" rounded="lg" />
      <BaseSkeleton class="h-4 w-3/4" />
    </div>
  </div>
  <EmptyState v-else-if="items.length === 0" :title="emptyTitle" :message="emptyMessage" />
  <div v-else class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
    <PosterCard
      v-for="item in items"
      :key="`${item.type}:${item.external_id}`"
      :content="item"
      :my-state="lookup?.[contentKey(item.type, item.external_id)]"
      class="!w-full"
    />
  </div>
</template>
