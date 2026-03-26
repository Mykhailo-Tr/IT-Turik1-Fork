import { createRouter, createWebHistory } from 'vue-router'

import Activate from '@/features/auth/views/ActivateView.vue'
import CompleteProfile from '@/features/auth/views/CompleteProfileView.vue'
import EditProfile from '@/features/profile/views/EditProfileView.vue'
import Home from '@/features/home/views/HomeView.vue'
import Login from '@/features/auth/views/LoginView.vue'
import Profile from '@/features/profile/views/ProfileView.vue'
import Register from '@/features/auth/views/RegisterView.vue'
import TeamsCreate from '@/features/teams/views/TeamsCreateView.vue'
import TeamsDetail from '@/features/teams/views/TeamsDetailView.vue'
import TeamsEdit from '@/features/teams/views/TeamsEditView.vue'
import Teams from '@/features/teams/views/TeamsView.vue'

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
    path: '/teams/create',
    component: TeamsCreate,
    meta: { requiresAuth: true },
  },
  {
    path: '/teams/:id/edit',
    component: TeamsEdit,
    meta: { requiresAuth: true },
  },
  {
    path: '/teams/:id',
    component: TeamsDetail,
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
