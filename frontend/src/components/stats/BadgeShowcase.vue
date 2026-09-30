<script setup lang="ts">
import { Award, BookOpen, Clapperboard, Compass, Heart, ListChecks, PenLine, Star, Target, Tv, Users } from 'lucide-vue-next'
import { useBadges } from '@/api/stats'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'

const props = defineProps<{ username: string }>()

const badges = useBadges(() => props.username)

const BADGE_ICONS: Record<string, unknown> = {
  Star, PenLine, Clapperboard, BookOpen, Tv, Compass, Users, Heart, ListChecks, Target,
}

function iconFor(name: string) {
  return BADGE_ICONS[name] ?? Award
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <h3 class="text-sm font-semibold text-fg">Rozetler</h3>
    <div v-if="badges.isPending.value" class="grid grid-cols-3 gap-3 sm:grid-cols-4">
      <BaseSkeleton v-for="i in 8" :key="i" class="h-24 w-full" rounded="lg" />
    </div>
    <div v-else class="grid grid-cols-3 gap-3 sm:grid-cols-4">
      <div
        v-for="badge in badges.data.value ?? []"
        :key="badge.key"
        class="flex flex-col items-center gap-1.5 rounded-card border border-border p-3 text-center"
        :class="badge.earned ? '' : 'opacity-40 grayscale'"
      >
        <component :is="iconFor(badge.icon)" class="size-6 text-link" />
        <p class="text-xs font-medium text-fg">{{ badge.name }}</p>
        <p v-if="!badge.earned" class="text-[10px] text-muted">{{ badge.progress.current }}/{{ badge.progress.target }}</p>
      </div>
    </div>
  </div>
</template>
