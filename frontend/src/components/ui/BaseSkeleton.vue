<script setup lang="ts">
withDefaults(defineProps<{ rounded?: 'sm' | 'md' | 'lg' | 'full' }>(), { rounded: 'md' })

const roundedClass: Record<string, string> = {
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-card',
  full: 'rounded-full',
}
</script>

<template>
  <span
    class="block animate-pulse bg-surface-2 motion-reduce:animate-none"
    :class="roundedClass[rounded]"
    aria-hidden="true"
  />
</template>
