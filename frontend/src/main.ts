import '@fontsource-variable/inter'
import 'vue-sonner/style.css'
import './styles/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { QueryClient, VueQueryPlugin } from '@tanstack/vue-query'
import { registerSW } from 'virtual:pwa-register'
import { toast } from 'vue-sonner'

import App from './App.vue'
import router from './router'
import { ApiError } from './api/client'
import { listenForInstallPrompt } from './composables/usePwaInstall'
import { useAuthStore } from './stores/auth'

const app = createApp(App)

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => error instanceof ApiError && error.status >= 500 && failureCount < 1,
    },
  },
})

app.use(createPinia())
app.use(router)
app.use(VueQueryPlugin, { queryClient })

listenForInstallPrompt()
app.mount('#app')

// Çevrimdışı açıldıysa profil alınamamıştır; bağlantı gelince sessizce tamamlanır (avatar, profil bağlantısı)
window.addEventListener('online', () => {
  const auth = useAuthStore()
  if (auth.token && !auth.me) auth.fetchMe().catch(() => undefined)
})

// Service worker yalnız üretim derlemesinde kaydolur (geliştirmede önbellek kafa karıştırmasın)
const updateServiceWorker = registerSW({
  onNeedRefresh() {
    toast.info('Yeni sürüm hazır', {
      description: 'Güncel KFDU’yu kullanmak için sayfayı yenile.',
      duration: Infinity,
      action: { label: 'Yenile', onClick: () => void updateServiceWorker(true) },
    })
  },
})
