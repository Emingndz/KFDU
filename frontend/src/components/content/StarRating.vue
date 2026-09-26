<script setup lang="ts">
import { computed, ref } from 'vue'
import { Star } from 'lucide-vue-next'

const props = withDefaults(
  defineProps<{
    modelValue: number | null
    readonly?: boolean
    size?: 'sm' | 'md' | 'lg'
  }>(),
  { readonly: false, size: 'md' },
)
const emit = defineEmits<{ 'update:modelValue': [value: number | null] }>()

const hoverValue = ref<number | null>(null)
const displayValue = computed(() => hoverValue.value ?? props.modelValue ?? 0)

const sizeClass: Record<string, string> = { sm: 'size-4', md: 'size-6', lg: 'size-8' }

function starFillWidth(starIndex: number): string {
  const starValue = displayValue.value - (starIndex - 1) * 2
  if (starValue >= 2) return '100%'
  if (starValue >= 1) return '50%'
  return '0%'
}

function setValue(value: number) {
  if (props.readonly) return
  emit('update:modelValue', props.modelValue === value ? null : value)
}

function onHalfEnter(value: number) {
  if (!props.readonly) hoverValue.value = value
}

function onKeydown(event: KeyboardEvent) {
  if (props.readonly) return
  const current = props.modelValue ?? 0
  if (event.key === 'ArrowRight' || event.key === 'ArrowUp') {
    event.preventDefault()
    emit('update:modelValue', Math.min(10, current + 1))
  } else if (event.key === 'ArrowLeft' || event.key === 'ArrowDown') {
    event.preventDefault()
    emit('update:modelValue', Math.max(1, current - 1))
  } else if (event.key === 'Home') {
    event.preventDefault()
    emit('update:modelValue', 1)
  } else if (event.key === 'End') {
    event.preventDefault()
    emit('update:modelValue', 10)
  } else if (event.key === 'Delete' || event.key === 'Backspace') {
    event.preventDefault()
    emit('update:modelValue', null)
  }
}
</script>

<template>
  <div
    class="inline-flex items-center gap-0.5 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
    :role="readonly ? undefined : 'slider'"
    :tabindex="readonly ? undefined : 0"
    :aria-valuemin="readonly ? undefined : 1"
    :aria-valuemax="readonly ? undefined : 10"
    :aria-valuenow="readonly || !modelValue ? undefined : modelValue"
    :aria-valuetext="modelValue ? `${modelValue}/10` : 'Puan verilmedi'"
    :aria-label="readonly ? undefined : 'Puan ver'"
    @keydown="onKeydown"
    @mouseleave="hoverValue = null"
  >
    <span v-for="starIndex in 5" :key="starIndex" class="relative inline-block" :class="sizeClass[size]">
      <Star class="absolute inset-0 size-full text-border" fill="none" />
      <span class="absolute inset-0 overflow-hidden" :style="{ width: starFillWidth(starIndex) }">
        <Star class="size-full text-star" fill="currentColor" />
      </span>
      <template v-if="!readonly">
        <button
          type="button"
          class="absolute inset-y-0 left-0 w-1/2 cursor-pointer"
          :aria-label="`${(starIndex - 1) * 2 + 1} puan ver`"
          tabindex="-1"
          @mouseenter="onHalfEnter((starIndex - 1) * 2 + 1)"
          @click="setValue((starIndex - 1) * 2 + 1)"
        />
        <button
          type="button"
          class="absolute inset-y-0 right-0 w-1/2 cursor-pointer"
          :aria-label="`${starIndex * 2} puan ver`"
          tabindex="-1"
          @mouseenter="onHalfEnter(starIndex * 2)"
          @click="setValue(starIndex * 2)"
        />
      </template>
    </span>
  </div>
</template>
