<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { toast } from 'vue-sonner'
import { Pencil } from 'lucide-vue-next'
import { useGoals, useSetGoals } from '@/api/stats'
import type { CatalogContentType } from '@/api/catalog'
import type { GoalOut } from '@/types'
import BaseButton from '@/components/ui/BaseButton.vue'

const props = defineProps<{ year: number }>()

const MEDIA_LABELS: Record<CatalogContentType, string> = { movie: 'film', tv: 'dizi', book: 'kitap' }
const RING_COLORS: Record<CatalogContentType, string> = { movie: '#3b82f6', tv: '#14b8a6', book: '#f97316' }
const RADIUS = 32
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

const goals = useGoals(() => props.year)
const setGoals = useSetGoals(() => props.year)

const editing = ref(false)
const drafts = ref<Record<string, number>>({ movie: 0, tv: 0, book: 0 })

function startEditing() {
  for (const goal of goals.data.value ?? []) drafts.value[goal.media_type] = goal.target
  editing.value = true
}

async function save() {
  const payload = Object.entries(drafts.value).map(([media_type, target]) => ({ media_type, target }))
  await setGoals.mutateAsync(payload)
  editing.value = false
}

let previousGoals: GoalOut[] | null = null
watch(goals.data, (newGoals) => {
  if (newGoals && previousGoals) {
    for (const goal of newGoals) {
      const prev = previousGoals.find((g) => g.media_type === goal.media_type)
      if (prev && goal.target > 0 && prev.current < prev.target && goal.current >= goal.target) {
        toast.success(`Tebrikler! ${props.year} ${MEDIA_LABELS[goal.media_type as CatalogContentType]} hedefini tamamladın 🎉`)
      }
    }
  }
  previousGoals = newGoals ?? null
})

const activeGoals = computed(() => (goals.data.value ?? []).filter((g) => g.target > 0))

function ringOffset(goal: GoalOut): number {
  const ratio = goal.target > 0 ? Math.min(goal.current / goal.target, 1) : 0
  return CIRCUMFERENCE * (1 - ratio)
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-semibold text-fg">{{ year }} Hedeflerim</h3>
      <button type="button" aria-label="Hedefleri düzenle" class="text-muted hover:text-fg" @click="editing ? (editing = false) : startEditing()">
        <Pencil class="size-4" />
      </button>
    </div>

    <div v-if="editing" class="flex flex-col gap-3 rounded-card border border-border p-4">
      <div v-for="type in (['movie', 'tv', 'book'] as CatalogContentType[])" :key="type" class="flex items-center justify-between gap-3">
        <label :for="`goal-${type}`" class="text-sm text-fg capitalize">{{ MEDIA_LABELS[type] }} hedefi</label>
        <input
          :id="`goal-${type}`"
          v-model.number="drafts[type]"
          type="number"
          min="0"
          class="h-9 w-24 rounded-lg border border-border bg-surface px-2 text-sm text-fg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
        />
      </div>
      <BaseButton size="sm" :loading="setGoals.isPending.value" @click="save">Kaydet</BaseButton>
    </div>

    <div v-else-if="activeGoals.length === 0" class="rounded-card border border-border p-4 text-sm text-muted">
      Henüz bir hedef belirlemedin. Kalem simgesine dokunarak yıllık hedef koyabilirsin.
    </div>
    <div v-else class="flex flex-wrap gap-6">
      <div v-for="goal in activeGoals" :key="goal.media_type" class="flex flex-col items-center gap-2">
        <svg width="80" height="80" viewBox="0 0 80 80" class="-rotate-90">
          <circle cx="40" cy="40" :r="RADIUS" fill="none" stroke="currentColor" class="text-surface-2" stroke-width="8" />
          <circle
            cx="40"
            cy="40"
            :r="RADIUS"
            fill="none"
            :stroke="RING_COLORS[goal.media_type as CatalogContentType]"
            stroke-width="8"
            stroke-linecap="round"
            :stroke-dasharray="CIRCUMFERENCE"
            :stroke-dashoffset="ringOffset(goal)"
            class="motion-safe:transition-all motion-safe:duration-500"
          />
        </svg>
        <p class="text-sm font-medium text-fg">{{ goal.current }}/{{ goal.target }}</p>
        <p class="text-xs text-muted capitalize">{{ MEDIA_LABELS[goal.media_type as CatalogContentType] }}</p>
      </div>
    </div>
  </div>
</template>
