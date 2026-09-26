<script setup lang="ts">
import BaseButton from './BaseButton.vue'

defineProps<{ message?: string }>()
defineEmits<{ retry: [] }>()
</script>

<template>
  <div class="flex flex-col items-center gap-3 px-6 py-16 text-center">
    <p class="text-lg font-semibold text-fg">Bir şeyler ters gitti</p>
    <p class="max-w-sm text-sm text-muted">{{ message ?? 'Beklenmeyen bir hata oluştu.' }}</p>
    <BaseButton variant="secondary" @click="$emit('retry')">Tekrar dene</BaseButton>
  </div>
</template>
