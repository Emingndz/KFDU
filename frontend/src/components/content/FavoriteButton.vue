<script setup lang="ts">
import { Heart } from 'lucide-vue-next'

defineProps<{ modelValue: boolean; disabled?: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()
</script>

<template>
  <button
    type="button"
    class="flex size-10 items-center justify-center rounded-lg border border-border text-muted transition hover:bg-surface-2 disabled:opacity-60"
    :class="modelValue ? 'border-like text-like' : ''"
    :disabled="disabled"
    :aria-pressed="modelValue"
    :aria-label="modelValue ? 'Favorilerden çıkar' : 'Favorilere ekle'"
    @click="emit('update:modelValue', !modelValue)"
  >
    <Heart class="size-5" :fill="modelValue ? 'currentColor' : 'none'" />
  </button>
</template>
