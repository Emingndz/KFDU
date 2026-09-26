<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ distribution: Record<string, number> }>()

const maxCount = computed(() => Math.max(1, ...Object.values(props.distribution)))
const bars = computed(() =>
  Array.from({ length: 10 }, (_, i) => {
    const value = i + 1
    const count = props.distribution[String(value)] ?? 0
    return { value, count, percent: (count / maxCount.value) * 100 }
  }),
)
</script>

<template>
  <div class="flex h-16 items-end gap-1" role="img" aria-label="Puan dağılımı histogramı">
    <div v-for="bar in bars" :key="bar.value" class="flex flex-1 flex-col items-center gap-1">
      <div
        class="w-full rounded-t bg-star/70"
        :style="{ height: `${bar.count > 0 ? Math.max(bar.percent, 4) : 0}%` }"
        :title="`${bar.value}/10 — ${bar.count} oy`"
      />
      <span class="text-[10px] text-muted">{{ bar.value }}</span>
    </div>
  </div>
</template>
