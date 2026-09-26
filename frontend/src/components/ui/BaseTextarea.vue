<script setup lang="ts">
import { useId } from 'vue'

defineProps<{
  label?: string
  hint?: string
  error?: string
  placeholder?: string
  maxlength?: number
  rows?: number
  disabled?: boolean
}>()

const model = defineModel<string>({ default: '' })
const id = useId()
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <label v-if="label" :for="id" class="text-sm font-medium text-fg">{{ label }}</label>
    <textarea
      :id="id"
      v-model="model"
      :placeholder="placeholder"
      :maxlength="maxlength"
      :rows="rows ?? 4"
      :disabled="disabled"
      :aria-invalid="Boolean(error)"
      class="w-full resize-y rounded-lg border border-border bg-surface px-3 py-2 text-sm text-fg placeholder:text-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500 disabled:opacity-60"
      :class="{ 'border-danger': error }"
    />
    <div class="flex items-center justify-between text-xs">
      <p v-if="error" class="text-danger">{{ error }}</p>
      <p v-else-if="hint" class="text-muted">{{ hint }}</p>
      <span v-else />
      <span v-if="maxlength" class="text-muted">{{ model.length }}/{{ maxlength }}</span>
    </div>
  </div>
</template>
