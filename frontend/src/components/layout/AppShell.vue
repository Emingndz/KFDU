<script setup lang="ts">
import AppBottomNav from './AppBottomNav.vue'
import AppHeader from './AppHeader.vue'
import RouteProgress from './RouteProgress.vue'
import OfflineBanner from './OfflineBanner.vue'
import ErrorBoundary from './ErrorBoundary.vue'
import ShortcutsHelpModal from './ShortcutsHelpModal.vue'
import { useKeyboardShortcuts } from '@/composables/useKeyboardShortcuts'

const { helpOpen } = useKeyboardShortcuts()
</script>

<template>
  <div class="flex min-h-dvh flex-col bg-bg text-fg">
    <OfflineBanner />
    <RouteProgress />
    <AppHeader />
    <main class="mx-auto w-full max-w-6xl flex-1 px-4 pb-20 sm:pb-8">
      <ErrorBoundary>
        <RouterView />
      </ErrorBoundary>
    </main>
    <footer class="border-t border-border px-4 py-6 text-center text-xs text-muted">
      <p>
        Bu ürün TMDB API'sini kullanır ancak TMDB tarafından onaylanmamış veya sertifikalandırılmamıştır. İzleme
        platformu verileri JustWatch tarafından sağlanır.
      </p>
      <p class="mt-1">Kitap verileri Open Library tarafından sağlanır.</p>
      <button type="button" class="mt-2 underline-offset-2 hover:text-fg hover:underline" @click="helpOpen = true">
        Klavye kısayolları
      </button>
    </footer>
    <AppBottomNav />
    <ShortcutsHelpModal v-model="helpOpen" />
  </div>
</template>
