<script setup lang="ts">
import { computed, ref } from 'vue'
import { useIntersectionObserver } from '@vueuse/core'
import { useMarkAllNotificationsRead, useNotifications, useUnreadNotificationsCount } from '@/api/social'
import { useNotificationClick } from '@/composables/useNotificationClick'
import { useFollowToggle } from '@/composables/useFollowToggle'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import NotificationRow from '@/components/notifications/NotificationRow.vue'

const notifications = useNotifications()
const unreadCount = useUnreadNotificationsCount()
const markAllRead = useMarkAllNotificationsRead()
const { open } = useNotificationClick()
const followToggle = useFollowToggle()

const items = computed(() => notifications.data.value?.pages.flatMap((p) => p.items) ?? [])

const sentinelRef = ref<HTMLElement | null>(null)
useIntersectionObserver(
  sentinelRef,
  ([entry]) => {
    if (entry?.isIntersecting && notifications.hasNextPage.value && !notifications.isFetchingNextPage.value) {
      void notifications.fetchNextPage()
    }
  },
  { rootMargin: '400px' },
)
</script>

<template>
  <div class="flex flex-col gap-4 py-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-fg">Bildirimler</h1>
      <button
        v-if="(unreadCount.data.value?.count ?? 0) > 0"
        type="button"
        class="text-sm font-medium text-link hover:underline"
        @click="markAllRead.mutate()"
      >
        Tümünü okundu say
      </button>
    </div>

    <div v-if="notifications.isPending.value" class="flex flex-col gap-2">
      <BaseSkeleton v-for="i in 5" :key="i" class="h-16 w-full" rounded="lg" />
    </div>
    <ErrorState v-else-if="notifications.isError.value" message="Bildirimler yüklenemedi." @retry="() => notifications.refetch()" />
    <EmptyState
      v-else-if="items.length === 0"
      title="Henüz bildirim yok"
      message="Birileri seni takip edince, aktivitini beğenince veya yorum yapınca burada göreceksin."
    />
    <template v-else>
      <div class="divide-y divide-border rounded-card border border-border">
        <NotificationRow
          v-for="notification in items"
          :key="notification.id"
          :notification="notification"
          :is-following-actor="followToggle.isFollowing(notification.actor.username)"
          :follow-pending="followToggle.isPending(notification.actor.username)"
          @click="open(notification)"
          @follow-back="followToggle.toggle(notification.actor.username)"
        />
      </div>
      <div ref="sentinelRef" />
      <div v-if="notifications.isFetchingNextPage.value" class="flex justify-center py-4"><BaseSkeleton class="h-16 w-full" rounded="lg" /></div>
      <BaseButton v-else-if="notifications.hasNextPage.value" variant="secondary" @click="notifications.fetchNextPage()">
        Daha fazla yükle
      </BaseButton>
    </template>
  </div>
</template>
