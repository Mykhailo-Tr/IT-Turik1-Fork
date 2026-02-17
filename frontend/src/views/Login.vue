<template>
  <div class="auth-page">
    <h2>Вхід у систему</h2>
    <form @submit.prevent="onLogin">
      <input v-model="form.username" placeholder="Логін" required />
      <input v-model="form.password" type="password" placeholder="Пароль" required />
      <button type="submit">Увійти</button>
    </form>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const auth = useAuthStore();
const router = useRouter();
const form = reactive({ username: '', password: '' });

const onLogin = async () => {
  try {
    await auth.login(form);
    router.push('/'); // Перехід на головну після успіху
  } catch (err) {
    alert('Помилка: перевірте дані');
  }
};
</script>