// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Activate from '../views/Activate.vue' // Імпортуємо новий компонент

const routes = [
  { 
    path: '/', 
    component: Home, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/login', 
    component: Login, 
    meta: { requiresGuest: true } 
  },
  { 
    path: '/register', 
    component: Register, 
    meta: { requiresGuest: true } 
  },
  { 
    // Одразу фіксуємо помилку: додаємо маршрут для активації
    // :uid та :token — це змінні, які ми потім забираємо через route.params
    path: '/activate/:uid/:token', 
    component: Activate,
    meta: { requiresGuest: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Захист роутів (Navigation Guards)
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access')

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && isAuthenticated && to.path !== '/activate') {
    // Якщо залогінений, не пускаємо на логін/реєстрацію
    next('/')
  } else {
    next()
  }
})

export default router