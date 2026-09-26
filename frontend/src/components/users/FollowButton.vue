<script setup lang="ts">
import { ref } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'

defineProps<{ isFollowing: boolean; pending?: boolean }>()
const emit = defineEmits<{ toggle: [] }>()

const hovering = ref(false)
</script>

<template>
  <BaseButton
    :variant="isFollowing ? 'secondary' : 'primary'"
    :loading="pending"
    :class="isFollowing && hovering ? '!bg-danger/15 !text-danger' : ''"
    @mouseenter="hovering = true"
    @mouseleave="hovering = false"
    @click="emit('toggle')"
  >
    {{ isFollowing ? (hovering ? 'Takipten Çık' : 'Takip Ediliyor') : 'Takip Et' }}
  </BaseButton>
</template>
