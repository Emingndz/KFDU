<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    src?: string | null
    name: string
    size?: 'sm' | 'md' | 'lg' | 'xl'
  }>(),
  { size: 'md' },
)

const sizeClass: Record<string, string> = {
  sm: 'size-8 text-xs',
  md: 'size-10 text-sm',
  lg: 'size-14 text-lg',
  xl: 'size-24 text-2xl',
}

const failed = ref(false)
watch(
  () => props.src,
  () => {
    failed.value = false
  },
)

const initials = computed(() => {
  const parts = props.name.trim().split(/\s+/).filter(Boolean)
  if (parts.length === 0) return '?'
  if (parts.length === 1) return parts[0]!.slice(0, 2).toUpperCase()
  return (parts[0]![0]! + parts[parts.length - 1]![0]!).toUpperCase()
})

const palette = [
  ['#7c5cff', '#5836e6'],
  ['#3b82f6', '#1d4ed8'],
  ['#14b8a6', '#0f766e'],
  ['#f97316', '#c2410c'],
  ['#f5b301', '#b45309'],
  ['#ff4d7d', '#be123c'],
]

const gradient = computed(() => {
  let hash = 0
  for (const char of props.name) hash = (hash * 31 + char.charCodeAt(0)) >>> 0
  const [from, to] = palette[hash % palette.length]!
  return `linear-gradient(135deg, ${from}, ${to})`
})

const showImage = computed(() => Boolean(props.src) && !failed.value)
</script>

<template>
  <span
    class="inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full font-semibold text-white select-none"
    :class="sizeClass[size]"
    :style="!showImage ? { background: gradient } : undefined"
  >
    <img
      v-if="showImage"
      :src="src!"
      :alt="name"
      loading="lazy"
      decoding="async"
      class="size-full object-cover"
      @error="failed = true"
    />
    <span v-else aria-hidden="true">{{ initials }}</span>
  </span>
</template>
