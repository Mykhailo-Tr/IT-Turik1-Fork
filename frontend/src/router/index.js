import { createRouter, createWebHistory } from 'vue-router'

import Activate from '../views/Activate.vue'
import CompleteProfile from '../views/CompleteProfile.vue'
import EditProfile from '../views/EditProfile.vue'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Profile from '../views/Profile.vue'
import Register from '../views/Register.vue'
import Teams from '../views/Teams.vue'

const routes = [
  {
    path: '/',
    component: Home,
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    component: Login,
    meta: { requiresGuest: true },
  },
  {
    path: '/register',
    component: Register,
    meta: { requiresGuest: true },
  },
  {
    path: '/profile',
    component: Profile,
    meta: { requiresAuth: true },
  },
  {
    path: '/profile/edit',
    component: EditProfile,
    meta: { requiresAuth: true },
  },
  {
    path: '/teams',
    component: Teams,
    meta: { requiresAuth: true },
  },
  {
    path: '/complete-profile',
    component: CompleteProfile,
    meta: { requiresAuth: true },
  },
  {
    path: '/activate/:uid/:token',
    component: Activate,
    meta: { requiresGuest: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access')
  const needsOnboarding = localStorage.getItem('needs_onboarding') === '1'

  if (isAuthenticated && needsOnboarding && to.path !== '/complete-profile') {
    next('/complete-profile')
    return
  }

  if (isAuthenticated && !needsOnboarding && to.path === '/complete-profile') {
    next('/')
    return
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }

  if (to.meta.requiresGuest && isAuthenticated && !to.path.startsWith('/activate/')) {
    next('/')
    return
  }

  next()
})

export default router
