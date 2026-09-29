<script setup lang="ts">
import { useOnline } from '@vueuse/core'

const isOnline = useOnline()
</script>

<template>
  <div v-if="!isOnline" role="status" class="bg-warning/15 px-4 py-2 text-center text-sm font-medium text-warning">
    İnternet bağlantın yok — bazı özellikler çalışmayabilir.
  </div>
</template>
