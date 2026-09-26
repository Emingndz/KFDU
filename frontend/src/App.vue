<script setup lang="ts">
import { Toaster } from 'vue-sonner'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
</script>

<template>
  <h1>You did it!</h1>
  <p>
    Visit <a href="https://vuejs.org/" target="_blank" rel="noopener">vuejs.org</a> to read the
    documentation
  </p>
  <Toaster rich-colors position="top-center" />
  <ConfirmDialog />
</template>

<style scoped></style>
