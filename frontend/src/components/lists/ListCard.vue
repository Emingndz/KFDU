<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { ListOut, MyListOut } from '@/types'

defineProps<{ list: ListOut | MyListOut }>()
</script>

<template>
  <RouterLink :to="`/liste/${list.id}`" class="flex flex-col gap-2 rounded-card border border-border p-3 hover:bg-surface-2">
    <div class="grid aspect-video grid-cols-2 gap-0.5 overflow-hidden rounded-lg bg-gradient-to-br from-brand-500/30 to-brand-700/30">
      <img v-for="(cover, i) in list.cover_urls.slice(0, 4)" :key="i" :src="cover" alt="" class="size-full object-cover" />
    </div>
    <div>
      <p class="font-medium text-fg">{{ list.title }}</p>
      <p class="text-xs text-muted">{{ list.item_count }} öğe · {{ list.is_public ? 'Herkese açık' : 'Gizli' }}</p>
    </div>
  </RouterLink>
</template>
