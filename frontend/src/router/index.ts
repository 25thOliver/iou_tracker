import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/ious',
      name: 'ious',
      component: () => import('@/views/IOUs.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/ious/create',
      name: 'iou-create',
      component: () => import('@/views/IOUForm.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/ious/:id',
      name: 'iou-detail',
      component: () => import('@/views/IOUDetail.vue'),
      meta: { requiresAuth: true },
      props: true
    },
    {
      path: '/ious/:id/edit',
      name: 'iou-edit',
      component: () => import('@/views/IOUForm.vue'),
      meta: { requiresAuth: true },
      props: true
    },
    {
      path: '/debts',
      name: 'debts',
      component: () => import('@/views/Debts.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/debts/create',
      name: 'debt-create',
      component: () => import('@/views/DebtForm.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/debts/:id',
      name: 'debt-detail',
      component: () => import('@/views/DebtDetail.vue'),
      meta: { requiresAuth: true },
      props: true
    },
    {
      path: '/debts/:id/edit',
      name: 'debt-edit',
      component: () => import('@/views/DebtForm.vue'),
      meta: { requiresAuth: true },
      props: true
    },
    {
      path: '/notifications',
      name: 'notifications',
      component: () => import('@/views/Notifications.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/Profile.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/Register.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFound.vue')
    }
  ]
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  
  // Check if route requires guest (not authenticated)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
    return
  }
  
  next()
})

export default router
