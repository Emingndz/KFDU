<script setup lang="ts">
import BaseModal from '@/components/ui/BaseModal.vue'

defineProps<{ trailerKey: string }>()
const open = defineModel<boolean>({ default: false })
</script>

<template>
  <BaseModal v-model="open" title="Fragman" size="lg">
    <div class="aspect-video w-full overflow-hidden rounded-lg bg-black">
      <iframe
        v-if="open"
        :src="`https://www.youtube-nocookie.com/embed/${trailerKey}?autoplay=1`"
        title="Fragman"
        class="size-full"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen
      />
    </div>
  </BaseModal>
</template>
