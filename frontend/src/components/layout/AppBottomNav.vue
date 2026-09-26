<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Compass, Rss, User } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <nav
    class="fixed inset-x-0 bottom-0 z-40 flex h-16 items-center justify-around border-t border-border bg-surface/95 backdrop-blur sm:hidden"
  >
    <RouterLink to="/" class="flex flex-col items-center gap-0.5 text-xs text-muted" active-class="text-brand-600">
      <Rss class="size-5" />
      Akış
    </RouterLink>
    <RouterLink to="/kesfet" class="flex flex-col items-center gap-0.5 text-xs text-muted" active-class="text-brand-600">
      <Compass class="size-5" />
      Keşfet
    </RouterLink>
    <RouterLink
      v-if="auth.me"
      :to="`/u/${auth.me.username}`"
      class="flex flex-col items-center gap-0.5 text-xs text-muted"
      active-class="text-brand-600"
    >
      <User class="size-5" />
      Profil
    </RouterLink>
  </nav>
</template>
