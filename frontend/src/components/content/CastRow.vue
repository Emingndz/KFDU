<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import type { Person } from '@/types'

defineProps<{ people: Person[] }>()

const failedPhotos = ref(new Set<string | number>())
</script>

<template>
  <div class="flex gap-4 overflow-x-auto pb-2">
    <component
      :is="person.id ? RouterLink : 'div'"
      v-for="person in people"
      :key="person.id ?? person.name"
      :to="person.id ? `/kisi/${person.id}` : undefined"
      class="flex w-20 shrink-0 flex-col items-center gap-1.5 text-center"
    >
      <img
        v-if="person.photo_url && !failedPhotos.has(person.id ?? person.name)"
        :src="person.photo_url"
        :alt="person.name"
        loading="lazy"
        decoding="async"
        class="size-20 rounded-full bg-surface-2 object-cover"
        @error="failedPhotos.add(person.id ?? person.name)"
      />
      <div v-else class="flex size-20 items-center justify-center rounded-full bg-surface-2 text-xs text-muted">
        {{ person.name.slice(0, 2).toUpperCase() }}
      </div>
      <p class="line-clamp-2 text-xs font-medium text-fg">{{ person.name }}</p>
      <p v-if="person.role" class="text-[10px] text-muted">{{ person.role }}</p>
    </component>
  </div>
</template>
