<script setup lang="ts">
import { ref, watch } from 'vue'
import { Heart } from 'lucide-vue-next'

const props = defineProps<{ modelValue: boolean; count: number; disabled?: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

const pulsing = ref(false)
watch(
  () => props.modelValue,
  (liked, wasLiked) => {
    if (liked && !wasLiked) {
      pulsing.value = true
      setTimeout(() => (pulsing.value = false), 300)
    }
  },
)
</script>

<template>
  <button
    type="button"
    class="flex items-center gap-1.5 text-sm text-muted transition disabled:cursor-not-allowed disabled:opacity-50"
    :class="modelValue ? 'text-like' : 'hover:text-fg'"
    :disabled="disabled"
    :aria-pressed="modelValue"
    :aria-label="`${modelValue ? 'Beğeniyi geri al' : 'Beğen'} · ${count}`"
    @click="emit('update:modelValue', !modelValue)"
  >
    <Heart class="size-5" :class="{ 'like-pulse': pulsing }" :fill="modelValue ? 'currentColor' : 'none'" />
    {{ count }}
  </button>
</template>

<style scoped>
@keyframes like-pulse-kf {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.35);
  }
  100% {
    transform: scale(1);
  }
}
.like-pulse {
  animation: like-pulse-kf 0.3s ease-out;
}
</style>
