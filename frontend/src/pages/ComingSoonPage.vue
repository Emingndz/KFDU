<script setup lang="ts">
withDefaults(defineProps<{ title?: string }>(), { title: 'Yakında' })
</script>

<template>
  <div class="mx-auto flex max-w-md flex-col items-center gap-2 px-6 py-24 text-center">
    <p class="text-lg font-semibold text-fg">{{ title }}</p>
    <p class="text-sm text-muted">Bu sayfa henüz yapım aşamasında.</p>
  </div>
</template>
