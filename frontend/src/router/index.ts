import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const devRoutes: RouteRecordRaw[] = import.meta.env.DEV
  ? [
      {
        path: '/_ui',
        name: 'ui-showcase',
        component: () => import('@/pages/UiShowcasePage.vue'),
      },
    ]
  : []

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [...devRoutes],
})

export default router
