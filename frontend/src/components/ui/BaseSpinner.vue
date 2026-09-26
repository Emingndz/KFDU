<script setup lang="ts">
withDefaults(defineProps<{ size?: 'sm' | 'md' | 'lg' }>(), { size: 'md' })

const sizeClass: Record<string, string> = { sm: 'size-4', md: 'size-6', lg: 'size-10' }
</script>

<template>
  <span
    class="inline-block animate-spin rounded-full border-2 border-border border-t-brand-500 motion-reduce:animate-none"
    :class="sizeClass[size]"
    role="status"
    aria-label="Yükleniyor"
  />
</template>
