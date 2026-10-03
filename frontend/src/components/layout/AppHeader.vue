<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { onClickOutside } from '@vueuse/core'
import { toast } from 'vue-sonner'
import { ChevronDown, Search } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import { usePwaInstall } from '@/composables/usePwaInstall'
import BaseAvatar from '@/components/ui/BaseAvatar.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import NotificationBell from '@/components/layout/NotificationBell.vue'

const auth = useAuthStore()
const router = useRouter()
const { mode, options: themeOptions } = useTheme()
const { canInstall, install } = usePwaInstall()

const menuOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)
onClickOutside(menuRef, () => (menuOpen.value = false))

function logout() {
  auth.logout()
  menuOpen.value = false
  router.push('/kesfet')
}

async function installApp() {
  if (await install()) toast.success('KFDU yüklendi — artık ana ekranından açabilirsin')
}
</script>

<template>
  <header class="sticky top-0 z-40 h-16 border-b border-border bg-surface/80 backdrop-blur">
    <div class="mx-auto flex h-full max-w-6xl items-center justify-between gap-4 px-4">
      <RouterLink to="/" class="flex items-center gap-2 font-bold text-fg">
        <span class="flex size-8 items-center justify-center rounded-lg bg-brand-600 text-sm text-white">K</span>
        KFDU
      </RouterLink>

      <nav class="hidden items-center gap-1 sm:flex">
        <RouterLink
          to="/"
          class="rounded-lg px-3 py-2 text-sm font-medium text-muted hover:bg-surface-2 hover:text-fg"
          active-class="bg-surface-2 text-fg"
        >
          Akış
        </RouterLink>
        <RouterLink
          to="/kesfet"
          class="rounded-lg px-3 py-2 text-sm font-medium text-muted hover:bg-surface-2 hover:text-fg"
          active-class="bg-surface-2 text-fg"
        >
          Keşfet
        </RouterLink>
      </nav>

      <div class="flex items-center gap-2">
        <button
          type="button"
          aria-label="Ara"
          class="flex size-10 items-center justify-center rounded-lg text-muted hover:bg-surface-2 hover:text-fg"
          @click="router.push('/kesfet')"
        >
          <Search class="size-5" />
        </button>

        <template v-if="auth.isAuthenticated">
          <NotificationBell />
          <div ref="menuRef" class="relative">
            <button
              type="button"
              class="flex items-center gap-1 rounded-lg p-1 hover:bg-surface-2"
              :aria-expanded="menuOpen"
              aria-haspopup="true"
              aria-label="Kullanıcı menüsü"
              @click="menuOpen = !menuOpen"
            >
              <BaseAvatar :name="auth.me?.display_name || auth.me?.username || '?'" :src="auth.me?.avatar_url" size="sm" />
              <ChevronDown class="size-4 text-muted" />
            </button>
            <div
              v-if="menuOpen"
              class="absolute right-0 mt-2 w-56 rounded-card border border-border bg-surface p-2 shadow-xl"
              role="menu"
              @click="menuOpen = false"
            >
              <RouterLink
                v-if="auth.me"
                :to="`/u/${auth.me.username}`"
                class="block rounded-lg px-3 py-2 text-sm text-fg hover:bg-surface-2"
                role="menuitem"
              >
                Profilim
              </RouterLink>
              <RouterLink to="/ayarlar" class="block rounded-lg px-3 py-2 text-sm text-fg hover:bg-surface-2" role="menuitem">
                Ayarlar
              </RouterLink>
              <button
                v-if="canInstall"
                type="button"
                role="menuitem"
                class="block w-full rounded-lg px-3 py-2 text-left text-sm text-fg hover:bg-surface-2"
                @click="installApp"
              >
                Uygulamayı yükle
              </button>
              <div class="my-1 border-t border-border" />
              <p class="px-3 pb-1 text-xs font-medium text-muted">Tema</p>
              <button
                v-for="option in themeOptions"
                :key="option.value"
                type="button"
                role="menuitem"
                class="block w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-surface-2"
                :class="mode === option.value ? 'font-medium text-link' : 'text-fg'"
                @click="mode = option.value"
              >
                {{ option.label }}
              </button>
              <div class="my-1 border-t border-border" />
              <button
                type="button"
                role="menuitem"
                class="block w-full rounded-lg px-3 py-2 text-left text-sm text-danger hover:bg-surface-2"
                @click="logout"
              >
                Çıkış yap
              </button>
            </div>
          </div>
        </template>
        <template v-else>
          <BaseButton variant="ghost" size="sm" to="/giris">Giriş</BaseButton>
          <BaseButton size="sm" to="/kayit">Kayıt ol</BaseButton>
        </template>
      </div>
    </div>
  </header>
</template>
