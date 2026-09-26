<script setup lang="ts">
import { computed } from 'vue'
import { Star } from 'lucide-vue-next'
import { formatRating } from '@/utils/format'

const props = withDefaults(defineProps<{ rating: number | null; size?: 'sm' | 'md' }>(), { size: 'md' })

const filledStars = computed(() => Math.round((props.rating ?? 0) / 2))
</script>

<template>
  <span v-if="rating" class="inline-flex items-center gap-1">
    <span class="flex">
      <Star
        v-for="i in 5"
        :key="i"
        :class="[size === 'sm' ? 'size-3' : 'size-4', i <= filledStars ? 'text-star' : 'text-border']"
        :fill="i <= filledStars ? 'currentColor' : 'none'"
      />
    </span>
    <span class="text-sm font-medium text-fg">{{ formatRating(rating) }}</span>
  </span>
  <span v-else class="text-sm text-muted">Puanlanmadı</span>
</template>
