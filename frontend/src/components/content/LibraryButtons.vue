<script setup lang="ts">
import { ref } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { Check, Clock, MoreHorizontal } from 'lucide-vue-next'
import type { CatalogContentType } from '@/api/catalog'
import type { LibraryStatus } from '@/types'
import { statusLabel } from '@/utils/content'
import BaseButton from '@/components/ui/BaseButton.vue'

defineProps<{ type: CatalogContentType; status: LibraryStatus | null; disabled?: boolean }>()
const emit = defineEmits<{ 'update:status': [value: LibraryStatus] }>()

const menuOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)
onClickOutside(menuRef, () => (menuOpen.value = false))

function select(status: LibraryStatus) {
  menuOpen.value = false
  emit('update:status', status)
}
</script>

<template>
  <div class="flex items-center gap-2">
    <BaseButton :variant="status === 'completed' ? 'primary' : 'secondary'" :disabled="disabled" @click="select('completed')">
      <template #icon><Check class="size-4" /></template>
      {{ statusLabel('completed', type) }}
    </BaseButton>
    <BaseButton :variant="status === 'planned' ? 'primary' : 'secondary'" :disabled="disabled" @click="select('planned')">
      <template #icon><Clock class="size-4" /></template>
      {{ statusLabel('planned', type) }}
    </BaseButton>
    <div ref="menuRef" class="relative">
      <button
        type="button"
        class="flex size-10 items-center justify-center rounded-lg border border-border text-muted hover:bg-surface-2 hover:text-fg disabled:opacity-60"
        :disabled="disabled"
        aria-label="Diğer durumlar"
        :aria-expanded="menuOpen"
        @click="menuOpen = !menuOpen"
      >
        <MoreHorizontal class="size-4" />
      </button>
      <div v-if="menuOpen" class="absolute right-0 z-10 mt-2 w-44 rounded-card border border-border bg-surface p-1 shadow-xl" role="menu">
        <button
          type="button"
          role="menuitem"
          class="block w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-surface-2"
          :class="status === 'in_progress' ? 'font-medium text-link' : 'text-fg'"
          @click="select('in_progress')"
        >
          {{ statusLabel('in_progress', type) }}
        </button>
        <button
          type="button"
          role="menuitem"
          class="block w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-surface-2"
          :class="status === 'dropped' ? 'font-medium text-link' : 'text-fg'"
          @click="select('dropped')"
        >
          {{ statusLabel('dropped', type) }}
        </button>
      </div>
    </div>
  </div>
</template>
