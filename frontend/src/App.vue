<template>
  <div id="app">
    <nav class="main-nav">
      <div class="nav-container">
        <router-link to="/" class="brand">🏆 TournamentOS</router-link>
        
        <div class="nav-links">
          <router-link to="/" class="nav-item">Головна</router-link>
          
          <template v-if="!isLoggedIn">
            <router-link to="/login" class="nav-item">Увійти</router-link>
            <router-link to="/register" class="nav-item btn-reg">Реєстрація</router-link>
          </template>
          
          <template v-else>
            <router-link to="/profile" class="nav-item">Мій профіль</router-link>
            <button @click="logout" class="nav-item btn-logout">Вийти</button>
          </template>
        </div> </div> </nav>

    <main class="page-content">
      <router-view @auth-change="checkAuth" />
    </main>
  </div> </template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const isLoggedIn = ref(false)
const router = useRouter()
const route = useRoute()

// Функція перевірки токена
const checkAuth = () => {
  isLoggedIn.value = !!localStorage.getItem('access')
}

// Слідкуємо за зміною шляху, щоб оновлювати стан навбару
watch(() => route.path, () => {
  checkAuth()
})

onMounted(() => {
  checkAuth()
})

const logout = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  checkAuth()
  router.push('/login')
}
</script>

<style>
:root {
  --primary: #4f46e5;
  --dark: #1f2937;
  --light: #f3f4f6;
  --danger: #ef4444;
}

body { margin: 0; font-family: 'Inter', sans-serif; background: var(--light); }

.main-nav {
  background: var(--dark);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.nav-container {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 1rem;
}

.brand { font-size: 1.5rem; font-weight: bold; text-decoration: none; color: white; }

.nav-links { display: flex; gap: 1.5rem; align-items: center; }

.nav-item { 
  text-decoration: none; 
  color: #d1d5db; 
  transition: 0.3s; 
  cursor: pointer; 
  border: none; 
  background: none; 
  font-size: 1rem; 
  font-weight: 500;
}

.nav-item:hover { color: white; }

.btn-reg { 
  background: var(--primary); 
  color: white; 
  padding: 0.5rem 1rem; 
  border-radius: 6px; 
}

.btn-logout { color: var(--danger); }
.btn-logout:hover { color: #f87171; }

.page-content { 
  max-width: 1000px; 
  margin: 2rem auto; 
  padding: 0 1rem; 
}

/* Стилі для карток (використовуємо в усіх views) */
.card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
}
</style>