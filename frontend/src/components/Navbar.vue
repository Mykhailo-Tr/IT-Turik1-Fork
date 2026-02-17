<template>
  <nav class="navbar">
    <div class="logo">MyProject</div>
    <div class="menu">
      <router-link to="/">Головна</router-link>
      
      <template v-if="!auth.isLoggedIn">
        <router-link to="/login">Увійти</router-link>
        <router-link to="/register" class="btn-reg">Реєстрація</router-link>
      </template>

      <template v-else>
        <span class="user-name">Привіт, {{ auth.user?.username || 'Користувач' }}</span>
        <button @click="handleLogout" class="btn-logout">Вийти</button>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const auth = useAuthStore();
const router = useRouter();

const handleLogout = () => {
  auth.logout();
  router.push('/login'); // Після виходу кидаємо на вхід
};
</script>

<style scoped>
.navbar { display: flex; justify-content: space-between; padding: 1rem 2rem; background: #333; color: white; }
.menu a { color: white; margin-left: 15px; text-decoration: none; }
.btn-reg { background: #42b983; padding: 5px 10px; border-radius: 4px; }
.btn-logout { background: #ff4d4d; border: none; color: white; cursor: pointer; margin-left: 15px; }
</style>