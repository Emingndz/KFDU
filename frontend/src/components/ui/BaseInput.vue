<script setup lang="ts">
import { computed, ref, useId } from 'vue'
import { Eye, EyeOff } from 'lucide-vue-next'

const props = withDefaults(
  defineProps<{
    label?: string
    hint?: string
    error?: string
    type?: string
    placeholder?: string
    maxlength?: number
    disabled?: boolean
    autocomplete?: string
  }>(),
  { type: 'text' },
)

const model = defineModel<string>({ default: '' })

defineOptions({ inheritAttrs: false })

const id = useId()
const showPassword = ref(false)
const isPassword = computed(() => props.type === 'password')
const resolvedType = computed(() => (isPassword.value && showPassword.value ? 'text' : props.type))
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <label v-if="label" :for="id" class="text-sm font-medium text-fg">{{ label }}</label>
    <div class="relative">
      <input
        :id="id"
        v-model="model"
        v-bind="$attrs"
        :type="resolvedType"
        :placeholder="placeholder"
        :maxlength="maxlength"
        :disabled="disabled"
        :autocomplete="autocomplete"
        :aria-invalid="Boolean(error)"
        class="h-10 w-full rounded-lg border border-border bg-surface px-3 text-sm text-fg placeholder:text-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500 disabled:opacity-60"
        :class="{ 'border-danger': error, 'pr-10': isPassword }"
      />
      <button
        v-if="isPassword"
        type="button"
        class="absolute inset-y-0 right-0 flex w-10 items-center justify-center text-muted hover:text-fg"
        :aria-label="showPassword ? 'Şifreyi gizle' : 'Şifreyi göster'"
        @click="showPassword = !showPassword"
      >
        <component :is="showPassword ? EyeOff : Eye" class="size-4" />
      </button>
    </div>
    <div class="flex items-center justify-between text-xs">
      <p v-if="error" class="text-danger">{{ error }}</p>
      <p v-else-if="hint" class="text-muted">{{ hint }}</p>
      <span v-else />
      <span v-if="maxlength" class="text-muted">{{ model.length }}/{{ maxlength }}</span>
    </div>
  </div>
</template>
