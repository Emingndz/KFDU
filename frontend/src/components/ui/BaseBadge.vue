<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'brand' | 'movie' | 'tv' | 'book' | 'success' | 'danger' | 'warning' | 'neutral'
    size?: 'sm' | 'md'
  }>(),
  { variant: 'neutral', size: 'md' },
)

const variantClass: Record<string, string> = {
  brand: 'bg-brand-500/15 text-link',
  movie: 'bg-movie/15 text-movie',
  tv: 'bg-tv/15 text-tv',
  book: 'bg-book/15 text-book',
  success: 'bg-success/15 text-success',
  danger: 'bg-danger/15 text-danger',
  warning: 'bg-warning/15 text-warning',
  neutral: 'bg-surface-2 text-muted',
}
</script>

<template>
  <span
    class="inline-flex items-center gap-1 rounded-full font-medium"
    :class="[variantClass[variant], size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-sm']"
  >
    <slot />
  </span>
</template>
