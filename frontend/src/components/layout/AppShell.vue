<script setup lang="ts">
import AppBottomNav from './AppBottomNav.vue'
import AppHeader from './AppHeader.vue'
import RouteProgress from './RouteProgress.vue'
</script>

<template>
  <div class="flex min-h-dvh flex-col bg-bg text-fg">
    <RouteProgress />
    <AppHeader />
    <main class="mx-auto w-full max-w-6xl flex-1 px-4 pb-20 sm:pb-8">
      <RouterView />
    </main>
    <footer class="border-t border-border px-4 py-6 text-center text-xs text-muted">
      <p>
        Bu ürün TMDB API'sini kullanır ancak TMDB tarafından onaylanmamış veya sertifikalandırılmamıştır. İzleme
        platformu verileri JustWatch tarafından sağlanır.
      </p>
      <p class="mt-1">Kitap verileri Open Library tarafından sağlanır.</p>
    </footer>
    <AppBottomNav />
  </div>
</template>
