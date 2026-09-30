<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Bell, Compass, Rss, User } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useUnreadNotificationsCount } from '@/api/social'

const auth = useAuthStore()
const unreadCount = useUnreadNotificationsCount()
</script>

<template>
  <nav
    class="fixed inset-x-0 bottom-0 z-40 flex h-16 items-center justify-around border-t border-border bg-surface/95 backdrop-blur sm:hidden"
  >
    <RouterLink to="/" class="flex flex-col items-center gap-0.5 text-xs text-muted" active-class="text-link">
      <Rss class="size-5" />
      Akış
    </RouterLink>
    <RouterLink to="/kesfet" class="flex flex-col items-center gap-0.5 text-xs text-muted" active-class="text-link">
      <Compass class="size-5" />
      Keşfet
    </RouterLink>
    <RouterLink
      v-if="auth.me"
      to="/bildirimler"
      class="relative flex flex-col items-center gap-0.5 text-xs text-muted"
      active-class="text-link"
    >
      <Bell class="size-5" />
      <span
        v-if="(unreadCount.data.value?.count ?? 0) > 0"
        class="absolute top-0 right-1/2 size-2 -translate-y-0.5 translate-x-3 rounded-full bg-danger"
        aria-hidden="true"
      />
      Bildirimler
    </RouterLink>
    <RouterLink
      v-if="auth.me"
      :to="`/u/${auth.me.username}`"
      class="flex flex-col items-center gap-0.5 text-xs text-muted"
      active-class="text-link"
    >
      <User class="size-5" />
      Profil
    </RouterLink>
  </nav>
</template>
