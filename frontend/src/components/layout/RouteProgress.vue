<script setup lang="ts">
import { routeLoading } from '@/composables/useRouteProgress'
</script>

<template>
  <div
    class="fixed inset-x-0 top-0 z-50 h-0.5 bg-brand-500 transition-opacity motion-safe:duration-200"
    :class="routeLoading ? 'opacity-100' : 'opacity-0'"
    aria-hidden="true"
  />
</template>
