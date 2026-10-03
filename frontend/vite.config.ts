import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

const DAY = 24 * 60 * 60

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    tailwindcss(),
    VitePWA({
      // Yeni sürüm kendiliğinden devreye girmez; kullanıcıya "Yenile" toast'u gösterilir (main.ts)
      registerType: 'prompt',
      injectRegister: false,
      includeAssets: ['favicon.svg', 'favicon.ico', 'apple-touch-icon-180x180.png'],
      manifest: {
        name: 'KFDU — Kitap, Film ve Dizi',
        short_name: 'KFDU',
        description: 'Film, dizi ve kitap kütüphaneni oluştur; puanla, incele, listeler yap ve arkadaşlarını takip et.',
        lang: 'tr',
        theme_color: '#7c5cff',
        background_color: '#0e1016',
        display: 'standalone',
        start_url: '/',
        scope: '/',
        icons: [
          { src: 'pwa-64x64.png', sizes: '64x64', type: 'image/png' },
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
          { src: 'maskable-icon-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        // Uygulama kabuğu (tüm sayfa parçaları, yazı tipi, ikonlar) çevrimdışı açılabilsin
        globPatterns: ['**/*.{js,css,html,svg,png,ico,woff2}'],
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/api\//, /^\/media\//],
        runtimeCaching: [
          {
            urlPattern: ({ url }) =>
              url.origin === 'https://image.tmdb.org' || url.origin === 'https://covers.openlibrary.org',
            handler: 'CacheFirst',
            options: {
              cacheName: 'kfdu-images',
              // Dış kaynaklı <img> yanıtları "opaque"tır (durum 0); kotada şişkin sayıldıkları için
              // kota aşılırsa önbellek kendiliğinden boşaltılır
              cacheableResponse: { statuses: [0, 200] },
              expiration: { maxEntries: 300, maxAgeSeconds: 30 * DAY, purgeOnQuotaError: true },
            },
          },
          {
            urlPattern: ({ url, request }) => request.method === 'GET' && url.pathname.startsWith('/api/v1/catalog/'),
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'kfdu-catalog',
              cacheableResponse: { statuses: [200] },
              expiration: { maxEntries: 500, maxAgeSeconds: DAY },
            },
          },
          {
            urlPattern: ({ url }) => url.pathname.startsWith('/api/'),
            handler: 'NetworkOnly',
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/media': 'http://127.0.0.1:8000',
    },
  },
})
