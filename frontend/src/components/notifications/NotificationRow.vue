<script setup lang="ts">
import type { NotificationOut } from '@/types'
import { notificationText } from '@/utils/notifications'
import { relativeTime } from '@/utils/format'
import BaseAvatar from '@/components/ui/BaseAvatar.vue'
import SafeImage from '@/components/ui/SafeImage.vue'

defineProps<{ notification: NotificationOut; isFollowingActor?: boolean; followPending?: boolean }>()
defineEmits<{ click: []; followBack: [] }>()
</script>

<template>
  <div class="flex w-full items-center gap-3 p-3 hover:bg-surface-2" :class="{ 'bg-brand-500/5': !notification.is_read }">
    <button type="button" class="flex min-w-0 flex-1 items-center gap-3 text-left" @click="$emit('click')">
      <BaseAvatar
        :name="notification.actor.display_name || notification.actor.username"
        :src="notification.actor.avatar_url"
        size="sm"
      />
      <div class="min-w-0 flex-1">
        <p class="line-clamp-2 text-sm text-fg">{{ notificationText(notification) }}</p>
        <p class="text-xs text-muted">{{ relativeTime(notification.created_at) }}</p>
      </div>
    </button>
    <button
      v-if="notification.type === 'follow' && !isFollowingActor"
      type="button"
      class="shrink-0 rounded-lg border border-border px-2.5 py-1.5 text-xs font-medium text-fg hover:bg-surface-2 disabled:opacity-60"
      :disabled="followPending"
      @click="$emit('followBack')"
    >
      Geri takip et
    </button>
    <SafeImage
      v-if="notification.content"
      :src="notification.content.poster_url"
      :alt="notification.content.title"
      class="aspect-[2/3] w-10 shrink-0 rounded object-cover"
    />
    <span v-if="!notification.is_read" class="size-2 shrink-0 rounded-full bg-brand-500" aria-hidden="true" />
  </div>
</template>
