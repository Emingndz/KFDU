<script setup lang="ts">
import BaseModal from './BaseModal.vue'
import BaseButton from './BaseButton.vue'
import { useConfirm } from '@/composables/useConfirm'

const { state, resolve } = useConfirm()
</script>

<template>
  <BaseModal
    :model-value="state.open"
    :title="state.title"
    size="sm"
    @update:model-value="(value) => !value && resolve(false)"
  >
    <p class="text-sm text-muted">{{ state.message }}</p>
    <template #footer>
      <BaseButton variant="secondary" @click="resolve(false)">{{ state.cancelText }}</BaseButton>
      <BaseButton :variant="state.danger ? 'danger' : 'primary'" @click="resolve(true)">
        {{ state.confirmText }}
      </BaseButton>
    </template>
  </BaseModal>
</template>
