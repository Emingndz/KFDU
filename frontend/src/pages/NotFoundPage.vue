<script setup lang="ts">
import BaseButton from '@/components/ui/BaseButton.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
</script>

<template>
  <EmptyState title="Burada hiçbir şey yok 🕵️" message="Aradığın sayfa taşınmış, silinmiş ya da hiç var olmamış olabilir.">
    <template #action>
      <div class="flex gap-3">
        <BaseButton variant="secondary" to="/">Akışa dön</BaseButton>
        <BaseButton to="/kesfet">Keşfet'e git</BaseButton>
      </div>
    </template>
  </EmptyState>
</template>
