<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { X } from 'lucide-vue-next'
import { useGenres } from '@/api/catalog'
import type { CatalogContentType, DiscoverFilters } from '@/api/catalog'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'

const props = defineProps<{ type: CatalogContentType; modelValue: DiscoverFilters }>()
const emit = defineEmits<{ 'update:modelValue': [value: DiscoverFilters] }>()

const SORT_OPTIONS = [
  { value: 'popular', label: 'Popülerlik' },
  { value: 'rating', label: 'Puan' },
  { value: 'newest', label: 'En yeni' },
  { value: 'oldest', label: 'En eski' },
]

const LANGUAGE_OPTIONS = [
  { value: 'tr', label: 'Türkçe' },
  { value: 'en', label: 'İngilizce' },
]

const genres = useGenres(() => props.type)
const genreOptions = computed(() => (genres.data.value ?? []).map((g) => ({ value: g.key, label: g.label })))

const draft = ref<DiscoverFilters>({ ...props.modelValue })
watch(
  () => props.modelValue,
  (value) => (draft.value = { ...value }),
)

const activeChips = computed(() => {
  const chips: { key: keyof DiscoverFilters; label: string }[] = []
  const value = props.modelValue
  if (value.genre) chips.push({ key: 'genre', label: genreOptions.value.find((g) => g.value === value.genre)?.label ?? value.genre })
  if (value.year_from) chips.push({ key: 'year_from', label: `${value.year_from}+` })
  if (value.year_to) chips.push({ key: 'year_to', label: `≤${value.year_to}` })
  if (value.min_rating) chips.push({ key: 'min_rating', label: `≥${value.min_rating} puan` })
  if (value.language) chips.push({ key: 'language', label: LANGUAGE_OPTIONS.find((l) => l.value === value.language)?.label ?? value.language })
  return chips
})

function apply() {
  emit('update:modelValue', { ...draft.value })
}

function clear() {
  draft.value = { sort: 'popular' }
  emit('update:modelValue', { sort: 'popular' })
}

function removeChip(key: keyof DiscoverFilters) {
  const next = { ...props.modelValue, [key]: undefined }
  draft.value = next
  emit('update:modelValue', next)
}
</script>

<template>
  <div class="flex flex-col gap-4 rounded-card border border-border p-4">
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
      <BaseSelect v-model="draft.genre" label="Tür" placeholder="Tümü" :options="genreOptions" />
      <div class="flex flex-col gap-1.5">
        <label class="text-sm font-medium text-fg">Yıl (min)</label>
        <input
          v-model.number="draft.year_from"
          type="number"
          placeholder="1990"
          class="h-10 w-full rounded-lg border border-border bg-surface px-3 text-sm text-fg placeholder:text-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
        />
      </div>
      <div class="flex flex-col gap-1.5">
        <label class="text-sm font-medium text-fg">Yıl (max)</label>
        <input
          v-model.number="draft.year_to"
          type="number"
          placeholder="2026"
          class="h-10 w-full rounded-lg border border-border bg-surface px-3 text-sm text-fg placeholder:text-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
        />
      </div>
      <div class="flex flex-col gap-1.5">
        <label class="text-sm font-medium text-fg">Asgari puan: {{ draft.min_rating ?? 0 }}</label>
        <input v-model.number="draft.min_rating" type="range" min="0" max="10" step="1" class="h-10 accent-brand-500" />
      </div>
      <BaseSelect v-model="draft.sort" label="Sıralama" :options="SORT_OPTIONS" />
      <BaseSelect v-model="draft.language" label="Dil" placeholder="Tümü" :options="LANGUAGE_OPTIONS" />
    </div>

    <div class="flex gap-2">
      <BaseButton size="sm" @click="apply">Uygula</BaseButton>
      <BaseButton size="sm" variant="ghost" @click="clear">Temizle</BaseButton>
    </div>

    <div v-if="activeChips.length > 0" class="flex flex-wrap gap-2">
      <button
        v-for="chip in activeChips"
        :key="chip.key"
        type="button"
        class="flex items-center gap-1 rounded-full bg-brand-500/15 px-3 py-1 text-xs font-medium text-brand-600"
        @click="removeChip(chip.key)"
      >
        {{ chip.label }}
        <X class="size-3" />
      </button>
    </div>
  </div>
</template>
