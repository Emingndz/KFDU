<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'

const props = withDefaults(defineProps<{ length?: number; disabled?: boolean }>(), {
  length: 6,
  disabled: false,
})
const emit = defineEmits<{ complete: [value: string] }>()

const model = defineModel<string>({ default: '' })

const boxes = ref<(HTMLInputElement | null)[]>([])
const digits = computed(() => {
  const arr = model.value.split('').slice(0, props.length)
  while (arr.length < props.length) arr.push('')
  return arr
})

function setBox(index: number, raw: string) {
  const char = raw.replace(/\D/g, '').slice(-1)
  const next = [...digits.value]
  next[index] = char
  const joined = next.join('')
  model.value = joined
  if (char && index < props.length - 1) {
    void nextTick(() => boxes.value[index + 1]?.focus())
  }
  if (joined.length === props.length && !joined.includes('')) emit('complete', joined)
}

function onKeydown(index: number, event: KeyboardEvent) {
  if (event.key === 'Backspace' && !digits.value[index] && index > 0) {
    event.preventDefault()
    const next = [...digits.value]
    next[index - 1] = ''
    model.value = next.join('')
    void nextTick(() => boxes.value[index - 1]?.focus())
  }
}

function onPaste(event: ClipboardEvent) {
  event.preventDefault()
  const clean = (event.clipboardData?.getData('text') ?? '').replace(/\D/g, '').slice(0, props.length)
  if (!clean) return
  model.value = clean
  void nextTick(() => boxes.value[Math.min(clean.length, props.length - 1)]?.focus())
  if (clean.length === props.length) emit('complete', clean)
}

watch(
  () => model.value,
  (value) => {
    if (value.length === 0) void nextTick(() => boxes.value[0]?.focus())
  },
)
</script>

<template>
  <div class="flex gap-2" role="group" aria-label="Doğrulama kodu">
    <input
      v-for="(digit, index) in digits"
      :key="index"
      :ref="(el) => (boxes[index] = el as HTMLInputElement | null)"
      :value="digit"
      type="text"
      inputmode="numeric"
      autocomplete="one-time-code"
      maxlength="1"
      :disabled="disabled"
      :aria-label="`Kodun ${index + 1}. hanesi`"
      class="h-12 w-10 rounded-lg border border-border bg-surface text-center text-lg font-semibold text-fg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500 disabled:opacity-60 sm:h-14 sm:w-12"
      @input="setBox(index, ($event.target as HTMLInputElement).value)"
      @keydown="onKeydown(index, $event)"
      @paste="onPaste"
    />
  </div>
</template>
