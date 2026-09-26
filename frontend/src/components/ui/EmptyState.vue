<script setup lang="ts">
defineProps<{ title: string; message?: string }>()
</script>

<template>
  <div class="flex flex-col items-center gap-3 px-6 py-16 text-center">
    <slot name="icon" />
    <p class="text-lg font-semibold text-fg">{{ title }}</p>
    <p v-if="message" class="max-w-sm text-sm text-muted">{{ message }}</p>
    <slot name="action" />
  </div>
</template>
