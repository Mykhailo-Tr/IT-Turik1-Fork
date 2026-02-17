<template>
  <div class="home-page">
    <h1>Головна сторінка</h1>
    
    <div v-if="auth.isLoggedIn" class="welcome-box">
      <p class="status success">Ви авторизовані як: <strong>{{ auth.user?.username }}</strong></p>
      
      <div class="api-message">
        <h3>Повідомлення з Django API:</h3>
        <p v-if="loading">Завантаження...</p>
        <p v-else class="msg-text">{{ secretMessage }}</p>
      </div>
    </div>

    <div v-else class="welcome-box">
      <p class="status warn">Ви переглядаєте сайт як гість. Будь ласка, увійдіть, щоб побачити секретне повідомлення.</p>
      <button @click="$router.push('/login')">Перейти до входу</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import api from '@/api'; // наш налаштований axios з interceptor

const auth = useAuthStore();
const secretMessage = ref('');
const loading = ref(false);

onMounted(async () => {
  if (auth.isLoggedIn) {
    loading.value = true;
    try {
      // Робимо запит до захищеного ендпоінту
      const response = await api.get('hello/'); // припустимо, там твій get_message
      secretMessage.value = response.data.message;
    } catch (err) {
      secretMessage.value = 'Не вдалося отримати повідомлення. Можливо, токен застарів.';
    } finally {
      loading.value = false;
    }
  }
});
</script>

<style scoped>
.home-page { text-align: center; margin-top: 40px; }
.welcome-box { padding: 20px; background: #f9f9f9; border-radius: 12px; display: inline-block; min-width: 300px; }
.status { padding: 10px; border-radius: 5px; }
.success { background: #e7f7ed; color: #2d8a4e; }
.warn { background: #fff4e5; color: #b7791f; }
.api-message { margin-top: 20px; border-top: 1px solid #ddd; padding-top: 10px; }
.msg-text { font-style: italic; color: #333; font-size: 1.2em; }
</style>