<script setup lang="ts">
import BaseModal from '@/components/ui/BaseModal.vue'

const open = defineModel<boolean>({ default: false })

const shortcuts = [
  { keys: ['/'], description: 'Aramaya git' },
  { keys: ['g', 'f'], description: 'Akışa git' },
  { keys: ['g', 'k'], description: "Keşfet'e git" },
  { keys: ['?'], description: 'Bu yardımı göster' },
]
</script>

<template>
  <BaseModal v-model="open" title="Klavye kısayolları" size="sm">
    <ul class="flex flex-col gap-3">
      <li v-for="shortcut in shortcuts" :key="shortcut.description" class="flex items-center justify-between gap-4 text-sm">
        <span class="text-fg">{{ shortcut.description }}</span>
        <span class="flex items-center gap-1">
          <template v-for="(key, i) in shortcut.keys" :key="i">
            <kbd class="rounded-md border border-border bg-surface-2 px-1.5 py-0.5 font-mono text-xs text-fg">{{ key }}</kbd>
            <span v-if="i < shortcut.keys.length - 1" class="text-muted">sonra</span>
          </template>
        </span>
      </li>
    </ul>
  </BaseModal>
</template>
