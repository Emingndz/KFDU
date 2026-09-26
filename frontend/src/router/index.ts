import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { routeLoading } from '@/composables/useRouteProgress'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    guestOnly?: boolean
    title?: string
  }
}

const ComingSoonPage = () => import('@/pages/ComingSoonPage.vue')

const devRoutes: RouteRecordRaw[] = import.meta.env.DEV
  ? [
      {
        path: '/_ui',
        name: 'ui-showcase',
        component: () => import('@/pages/UiShowcasePage.vue'),
      },
    ]
  : []

const routes: RouteRecordRaw[] = [
  {
    path: '/giris',
    name: 'login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: { guestOnly: true, title: 'Giriş yap' },
  },
  {
    path: '/kayit',
    name: 'register',
    component: () => import('@/pages/RegisterPage.vue'),
    meta: { guestOnly: true, title: 'Kayıt ol' },
  },
  {
    path: '/sifremi-unuttum',
    name: 'forgot-password',
    component: () => import('@/pages/ForgotPasswordPage.vue'),
    meta: { guestOnly: true, title: 'Şifremi unuttum' },
  },
  {
    path: '/hosgeldin',
    name: 'onboarding',
    component: () => import('@/pages/OnboardingPage.vue'),
    meta: { requiresAuth: true, title: 'Hoş geldin' },
  },
  {
    path: '/',
    name: 'feed',
    component: ComingSoonPage,
    props: { title: 'Akış' },
    meta: { title: 'Akış' },
  },
  {
    path: '/kesfet',
    name: 'discover',
    component: () => import('@/pages/DiscoverPage.vue'),
    meta: { title: 'Keşfet' },
  },
  {
    path: '/film/:id',
    name: 'movie-detail',
    component: ComingSoonPage,
    props: { title: 'Film' },
    meta: { title: 'Film' },
  },
  {
    path: '/kitap/:id',
    name: 'book-detail',
    component: ComingSoonPage,
    props: { title: 'Kitap' },
    meta: { title: 'Kitap' },
  },
  {
    path: '/dizi/:id',
    name: 'tv-detail',
    component: ComingSoonPage,
    props: { title: 'Dizi' },
    meta: { title: 'Dizi' },
  },
  {
    path: '/inceleme/:id',
    name: 'review',
    component: ComingSoonPage,
    props: { title: 'İnceleme' },
    meta: { title: 'İnceleme' },
  },
  {
    path: '/u/:username',
    name: 'profile',
    component: ComingSoonPage,
    props: { title: 'Profil' },
    meta: { title: 'Profil' },
  },
  {
    path: '/liste/:id',
    name: 'list',
    component: ComingSoonPage,
    props: { title: 'Liste' },
    meta: { title: 'Liste' },
  },
  {
    path: '/ayarlar',
    name: 'settings',
    component: ComingSoonPage,
    props: { title: 'Ayarlar' },
    meta: { requiresAuth: true, title: 'Ayarlar' },
  },
  {
    path: '/bildirimler',
    name: 'notifications',
    component: ComingSoonPage,
    props: { title: 'Bildirimler' },
    meta: { requiresAuth: true, title: 'Bildirimler' },
  },
  {
    path: '/kisi/:id',
    name: 'person',
    component: ComingSoonPage,
    props: { title: 'Kişi' },
    meta: { title: 'Kişi' },
  },
  {
    path: '/yazar/:id',
    name: 'author',
    component: ComingSoonPage,
    props: { title: 'Yazar' },
    meta: { title: 'Yazar' },
  },
  {
    path: '/ozet/:year?',
    name: 'wrapped',
    component: ComingSoonPage,
    props: { title: 'Yıllık Özet' },
    meta: { requiresAuth: true, title: 'Yıllık Özet' },
  },
  {
    path: '/oneriler',
    name: 'recommendations',
    component: ComingSoonPage,
    props: { title: 'Öneriler' },
    meta: { requiresAuth: true, title: 'Öneriler' },
  },
  {
    path: '/asistan/:conversationId?',
    name: 'assistant',
    component: ComingSoonPage,
    props: { title: 'KFDU Asistan' },
    meta: { requiresAuth: true, title: 'KFDU Asistan' },
  },
  ...devRoutes,
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: ComingSoonPage,
    props: { title: 'Sayfa bulunamadı' },
    meta: { title: 'Sayfa bulunamadı' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash }
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  routeLoading.value = true
  const auth = useAuthStore()

  if (auth.token && !auth.me) {
    try {
      await auth.fetchMe()
    } catch {
      return { path: '/giris', query: { redirect: to.fullPath } }
    }
  }

  if (to.path === '/' && !auth.isAuthenticated) {
    return { path: '/kesfet' }
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { path: '/giris', query: { redirect: to.fullPath } }
  }

  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { path: '/' }
  }

  return true
})

router.afterEach((to) => {
  routeLoading.value = false
  document.title = to.meta.title ? `${to.meta.title} · KFDU` : 'KFDU'
})

router.onError(() => {
  routeLoading.value = false
})

export default router
