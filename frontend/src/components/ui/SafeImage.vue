<script setup lang="ts">
import { ref, watch } from 'vue'
import { ImageOff } from 'lucide-vue-next'

const props = defineProps<{ src?: string | null; alt: string }>()

const failed = ref(false)
watch(
  () => props.src,
  () => (failed.value = false),
)
</script>

<template>
  <img v-if="src && !failed" :src="src" :alt="alt" loading="lazy" decoding="async" @error="failed = true" />
  <div v-else class="flex items-center justify-center bg-surface-2 text-muted">
    <ImageOff class="size-1/3" />
  </div>
</template>
