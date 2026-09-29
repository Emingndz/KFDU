<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { PublicUserOut } from '@/types'
import BaseAvatar from '@/components/ui/BaseAvatar.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

defineProps<{ user: PublicUserOut; isFollowing?: boolean; followPending?: boolean }>()
defineEmits<{ toggleFollow: [] }>()
</script>

<template>
  <div class="flex items-center gap-3 rounded-card border border-border p-3">
    <RouterLink :to="`/u/${user.username}`" :aria-label="`${user.display_name || user.username} profili`">
      <BaseAvatar :name="user.display_name || user.username" :src="user.avatar_url" size="md" />
    </RouterLink>
    <div class="min-w-0 flex-1">
      <RouterLink :to="`/u/${user.username}`" class="block truncate text-sm font-medium text-fg hover:underline">
        {{ user.display_name || user.username }}
      </RouterLink>
      <p class="truncate text-xs text-muted">@{{ user.username }}</p>
      <p v-if="user.bio" class="mt-1 line-clamp-2 text-xs text-muted">{{ user.bio }}</p>
    </div>
    <BaseButton
      size="sm"
      :variant="isFollowing ? 'secondary' : 'primary'"
      :loading="followPending"
      @click="$emit('toggleFollow')"
    >
      {{ isFollowing ? 'Takip ediliyor' : 'Takip et' }}
    </BaseButton>
  </div>
</template>
