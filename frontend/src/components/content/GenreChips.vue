<script setup lang="ts">
defineProps<{ genres: string[] }>()
</script>

<template>
  <div class="flex flex-wrap gap-1.5">
    <span v-for="genre in genres" :key="genre" class="rounded-full bg-surface-2 px-2.5 py-1 text-xs font-medium text-muted">
      {{ genre }}
    </span>
  </div>
</template>
