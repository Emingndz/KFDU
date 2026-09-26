<script setup lang="ts">
import { ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { ImageOff } from 'lucide-vue-next'
import type { ContentSummary } from '@/types'
import { contentPath, typeLabel } from '@/utils/content'
import BaseBadge from '@/components/ui/BaseBadge.vue'

const props = withDefaults(
  defineProps<{
    content: ContentSummary
    myState?: { isFavorite?: boolean } | null
    size?: 'sm' | 'md' | 'lg'
  }>(),
  { size: 'md' },
)

const failed = ref(false)
watch(
  () => props.content.poster_url,
  () => (failed.value = false),
)

const widthClass: Record<string, string> = { sm: 'w-28', md: 'w-36', lg: 'w-44' }
const badgeVariant: Record<string, 'movie' | 'tv' | 'book'> = { movie: 'movie', tv: 'tv', book: 'book' }
</script>

<template>
  <RouterLink
    :to="contentPath(content.type, content.external_id)"
    class="group flex flex-col gap-1.5"
    :class="widthClass[size]"
  >
    <div class="relative aspect-[2/3] overflow-hidden rounded-card bg-surface-2">
      <img
        v-if="content.poster_url && !failed"
        :src="content.poster_url"
        :alt="content.title"
        loading="lazy"
        decoding="async"
        class="size-full object-cover transition motion-safe:duration-200 group-hover:scale-105"
        @error="failed = true"
      />
      <div v-else class="flex size-full flex-col items-center justify-center gap-1 p-2 text-center text-muted">
        <ImageOff class="size-6" />
        <span class="line-clamp-3 text-xs">{{ content.title }}</span>
      </div>
      <BaseBadge :variant="badgeVariant[content.type]" size="sm" class="absolute top-1.5 left-1.5">
        {{ typeLabel(content.type) }}
      </BaseBadge>
      <BaseBadge v-if="myState?.isFavorite" variant="danger" size="sm" class="absolute top-1.5 right-1.5">
        ♥
      </BaseBadge>
    </div>
    <div>
      <p class="line-clamp-2 text-sm font-medium text-fg">{{ content.title }}</p>
      <p class="text-xs text-muted">{{ content.year ?? '—' }}</p>
    </div>
  </RouterLink>
</template>
