<script setup lang="ts">
import { ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { ImageOff } from 'lucide-vue-next'

const props = defineProps<{ to: string; title: string; posterUrl?: string | null; year?: number | null }>()

const failed = ref(false)
watch(
  () => props.posterUrl,
  () => (failed.value = false),
)
</script>

<template>
  <RouterLink :to="to" class="group flex w-full flex-col gap-1.5">
    <div class="relative aspect-[2/3] overflow-hidden rounded-card bg-surface-2">
      <img
        v-if="posterUrl && !failed"
        :src="posterUrl"
        :alt="title"
        loading="lazy"
        decoding="async"
        class="size-full object-cover transition motion-safe:duration-200 group-hover:scale-105"
        @error="failed = true"
      />
      <div v-else class="flex size-full flex-col items-center justify-center gap-1 p-2 text-center text-muted">
        <ImageOff class="size-6" />
        <span class="line-clamp-3 text-xs">{{ title }}</span>
      </div>
    </div>
    <div>
      <p class="line-clamp-2 text-sm font-medium text-fg">{{ title }}</p>
      <p class="text-xs text-muted">{{ year ?? '—' }}</p>
    </div>
  </RouterLink>
</template>
