import { createRouter, createWebHistory } from 'vue-router'

import Activate from '@/features/auth/views/ActivateView.vue'
import RoleCodesAdmin from '@/features/admin/views/RoleCodesAdminView.vue'
import CompleteProfile from '@/features/auth/views/CompleteProfileView.vue'
import ForgotPassword from '@/features/auth/views/ForgotPasswordView.vue'
import EditProfile from '@/features/profile/views/EditProfileView.vue'
import Home from '@/features/home/views/HomeView.vue'
import Login from '@/features/auth/views/LoginView.vue'
import Profile from '@/features/profile/views/ProfileView.vue'
import Register from '@/features/auth/views/RegisterView.vue'
import ResetPassword from '@/features/auth/views/ResetPasswordView.vue'
import TeamsCreate from '@/features/teams/views/TeamsCreateView.vue'
import TeamsDetail from '@/features/teams/views/TeamsDetailView.vue'
import TeamsEdit from '@/features/teams/views/TeamsEditView.vue'
import Teams from '@/features/teams/views/TeamsView.vue'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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
      path: '/forgot-password',
      component: ForgotPassword,
    },
    {
      path: '/reset-password/:uid/:token',
      component: ResetPassword,
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
      path: '/users/:id',
      component: () => import('@/features/profile/views/UserProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/admin/role-codes',
      component: RoleCodesAdmin,
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
  ],
})

router.beforeEach(async (to, _from, next) => {
  const store = useUserStore()
  const tokens = store.getTokens()

  const isAuthenticated = !!tokens.access
  const needsOnboarding = !!tokens.needsOnboarding

  if (isAuthenticated && needsOnboarding && to.path !== '/complete-profile') {
    next('/complete-profile')
    return
  }

  if (isAuthenticated && !needsOnboarding && to.path === '/complete-profile') {
    next('/')
    return
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    store.logout()
    next('/login')
    return
  }

  if (
    to.meta.requiresGuest &&
    isAuthenticated &&
    !to.path.startsWith('/activate/') &&
    !to.path.startsWith('/reset-password/')
  ) {
    next('/')
    return
  }

  next()
})

export default router
