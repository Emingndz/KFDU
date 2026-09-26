<script setup lang="ts">
import { computed } from 'vue'
import type { Providers } from '@/types'

const props = defineProps<{ providers: Providers }>()

const groups = computed(() => [
  { label: 'Abonelik', names: props.providers.flatrate ?? [] },
  { label: 'Kiralık', names: props.providers.rent ?? [] },
  { label: 'Satın Al', names: props.providers.buy ?? [] },
])
const hasAny = computed(() => groups.value.some((g) => g.names.length > 0))
</script>

<template>
  <div v-if="hasAny" class="flex flex-col gap-3">
    <div v-for="group in groups" :key="group.label" v-show="group.names.length > 0" class="flex flex-col gap-1">
      <p class="text-xs font-medium text-muted">{{ group.label }}</p>
      <div class="flex flex-wrap gap-2">
        <span v-for="name in group.names" :key="name" class="rounded-lg bg-surface-2 px-2.5 py-1 text-sm text-fg">
          {{ name }}
        </span>
      </div>
    </div>
    <p class="text-[10px] text-muted">Veriler JustWatch tarafından sağlanır.</p>
  </div>
</template>
