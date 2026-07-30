import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { requiresAuth: true } },
  { path: '/menu', name: 'Menu', component: () => import('../views/Menu.vue'), meta: { requiresAuth: true } },
  { path: '/attendance', name: 'Attendance', component: () => import('../views/Attendance.vue'), meta: { requiresAuth: true } },
  { path: '/reports', name: 'Reports', component: () => import('../views/Reports.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/expenses', name: 'Expenses', component: () => import('../views/Expenses.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/users', name: 'Users', component: () => import('../views/Users.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin', name: 'AdminConfig', component: () => import('../views/AdminConfig.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/ratings', name: 'Ratings', component: () => import('../views/Ratings.vue'), meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: () => import('../views/Profile.vue'), meta: { requiresAuth: true } },
]

const router = createRouter({ history: createWebHashHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  if (to.meta.requiresAuth && !token) return next('/login')
  if (to.meta.requiresAdmin && user.role !== 'admin') return next('/dashboard')
  next()
})

export default router
