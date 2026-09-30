<script setup lang="ts">
import SafeImage from '@/components/ui/SafeImage.vue'
import type { SeasonOut } from '@/types'

defineProps<{ seasons: SeasonOut[] }>()
</script>

<template>
  <div class="flex gap-4 overflow-x-auto pb-2">
    <div v-for="season in seasons" :key="season.number" class="flex w-28 shrink-0 flex-col gap-1.5">
      <SafeImage :src="season.poster_url" :alt="season.name" class="aspect-[2/3] w-28 rounded-card object-cover" />
      <p class="line-clamp-2 text-xs font-medium text-fg">{{ season.name }}</p>
      <p class="text-[10px] text-muted">
        {{ season.episode_count }} bölüm<template v-if="season.air_year"> · {{ season.air_year }}</template>
      </p>
    </div>
  </div>
</template>
