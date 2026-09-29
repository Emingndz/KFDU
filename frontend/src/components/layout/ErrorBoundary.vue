<script setup lang="ts">
import { onErrorCaptured, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import BaseButton from '@/components/ui/BaseButton.vue'

const route = useRoute()
const failed = ref(false)

onErrorCaptured((error) => {
  failed.value = true
  console.error(error)
  return false
})

watch(
  () => route.fullPath,
  () => (failed.value = false),
)

function reload() {
  window.location.reload()
}
</script>

<template>
  <div v-if="failed" class="flex flex-col items-center gap-3 px-6 py-24 text-center">
    <p class="text-lg font-semibold text-fg">Bir şeyler ters gitti</p>
    <p class="max-w-sm text-sm text-muted">Sayfa beklenmedik bir hatayla karşılaştı.</p>
    <BaseButton @click="reload">Sayfayı yenile</BaseButton>
  </div>
  <slot v-else />
</template>
