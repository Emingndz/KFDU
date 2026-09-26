<script setup lang="ts">
import { Toaster } from 'vue-sonner'
import AppShell from '@/components/layout/AppShell.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
</script>

<template>
  <AppShell />
  <Toaster rich-colors position="top-center" />
  <ConfirmDialog />
</template>
