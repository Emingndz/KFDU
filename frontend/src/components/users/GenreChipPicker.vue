<script setup lang="ts">
defineProps<{ genres: { key: string; label: string }[]; selected: Set<string> }>()
const emit = defineEmits<{ toggle: [key: string] }>()
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <button
      v-for="genre in genres"
      :key="genre.key"
      type="button"
      class="rounded-full border px-3 py-1.5 text-sm transition motion-safe:duration-150"
      :class="
        selected.has(genre.key)
          ? 'border-brand-500 bg-brand-500/15 text-brand-600'
          : 'border-border bg-surface text-fg hover:bg-surface-2'
      "
      :aria-pressed="selected.has(genre.key)"
      @click="emit('toggle', genre.key)"
    >
      {{ genre.label }}
    </button>
  </div>
</template>
