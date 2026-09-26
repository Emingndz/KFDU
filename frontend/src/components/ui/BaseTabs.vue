<script setup lang="ts">
const props = defineProps<{ tabs: { value: string; label: string }[] }>()
const model = defineModel<string>({ required: true })

function onKeydown(event: KeyboardEvent) {
  const currentIndex = props.tabs.findIndex((tab) => tab.value === model.value)
  if (event.key === 'ArrowRight') {
    event.preventDefault()
    model.value = props.tabs[(currentIndex + 1) % props.tabs.length]!.value
  } else if (event.key === 'ArrowLeft') {
    event.preventDefault()
    model.value = props.tabs[(currentIndex - 1 + props.tabs.length) % props.tabs.length]!.value
  }
}
</script>

<template>
  <div role="tablist" class="flex gap-1 border-b border-border" @keydown="onKeydown">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      role="tab"
      type="button"
      :aria-selected="model === tab.value"
      :tabindex="model === tab.value ? 0 : -1"
      class="border-b-2 px-4 py-2 text-sm font-medium transition motion-safe:duration-150"
      :class="
        model === tab.value
          ? 'border-brand-500 text-fg'
          : 'border-transparent text-muted hover:text-fg'
      "
      @click="model = tab.value"
    >
      {{ tab.label }}
    </button>
  </div>
</template>
