<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { onClickOutside } from '@vueuse/core'
import { Bell } from 'lucide-vue-next'
import { useMarkAllNotificationsRead, useNotifications, useUnreadNotificationsCount } from '@/api/social'
import { useNotificationClick } from '@/composables/useNotificationClick'
import { useFollowToggle } from '@/composables/useFollowToggle'
import type { NotificationOut } from '@/types'
import BaseSpinner from '@/components/ui/BaseSpinner.vue'
import NotificationRow from '@/components/notifications/NotificationRow.vue'

const panelOpen = ref(false)
const panelRef = ref<HTMLElement | null>(null)
onClickOutside(panelRef, () => (panelOpen.value = false))

const unreadCount = useUnreadNotificationsCount()
const notifications = useNotifications()
const items = computed(() => notifications.data.value?.pages.flatMap((p) => p.items).slice(0, 10) ?? [])

const markAllRead = useMarkAllNotificationsRead()
const { open } = useNotificationClick()
const followToggle = useFollowToggle()

function openNotification(notification: NotificationOut) {
  panelOpen.value = false
  open(notification)
}
</script>

<template>
  <div ref="panelRef" class="relative">
    <button
      type="button"
      class="relative flex size-10 items-center justify-center rounded-lg text-muted hover:bg-surface-2 hover:text-fg"
      aria-label="Bildirimler"
      :aria-expanded="panelOpen"
      aria-haspopup="true"
      @click="panelOpen = !panelOpen"
    >
      <Bell class="size-5" />
      <span
        v-if="(unreadCount.data.value?.count ?? 0) > 0"
        class="absolute top-1.5 right-1.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-danger px-1 text-[10px] font-medium text-white"
      >
        {{ unreadCount.data.value!.count > 9 ? '9+' : unreadCount.data.value!.count }}
      </span>
    </button>

    <div v-if="panelOpen" class="absolute right-0 z-50 mt-2 w-80 rounded-card border border-border bg-surface shadow-xl">
      <div class="flex items-center justify-between border-b border-border p-3">
        <p class="text-sm font-semibold text-fg">Bildirimler</p>
        <button
          v-if="(unreadCount.data.value?.count ?? 0) > 0"
          type="button"
          class="text-xs font-medium text-link hover:underline"
          @click="markAllRead.mutate()"
        >
          Tümünü okundu say
        </button>
      </div>
      <div class="max-h-96 overflow-y-auto">
        <div v-if="notifications.isPending.value" class="flex justify-center py-6"><BaseSpinner /></div>
        <p v-else-if="items.length === 0" class="p-4 text-center text-sm text-muted">Henüz bildirim yok</p>
        <div v-else class="divide-y divide-border">
          <NotificationRow
            v-for="notification in items"
            :key="notification.id"
            :notification="notification"
            :is-following-actor="followToggle.isFollowing(notification.actor.username)"
            :follow-pending="followToggle.isPending(notification.actor.username)"
            @click="openNotification(notification)"
            @follow-back="followToggle.toggle(notification.actor.username)"
          />
        </div>
      </div>
      <RouterLink
        to="/bildirimler"
        class="block border-t border-border p-3 text-center text-sm font-medium text-link hover:underline"
        @click="panelOpen = false"
      >
        Tümünü gör
      </RouterLink>
    </div>
  </div>
</template>
