<template>
  <div class="auth-card">
    <h2>Створити акаунт</h2>
    <form @submit.prevent="onRegister">
      <div class="form-group">
        <label>Логін:</label>
        <input v-model="form.username" type="text" required placeholder="Ваш нікнейм" />
      </div>
      
      <div class="form-group">
        <label>Email:</label>
        <input v-model="form.email" type="email" required placeholder="example@mail.com" />
      </div>

      <div class="form-group">
        <label>Пароль:</label>
        <input v-model="form.password" type="password" required placeholder="Мінімум 8 символів" />
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? 'Реєстрація...' : 'Зареєструватися' }}
      </button>
    </form>
    
    <p class="switch-mode">
      Вже маєте акаунт? <router-link to="/login">Увійдіть тут</router-link>
    </p>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const auth = useAuthStore();
const router = useRouter();
const loading = ref(false);

const form = reactive({
  username: '',
  email: '',
  password: ''
});

const onRegister = async () => {
  loading.value = true;
  try {
    await auth.register(form);
    alert('Акаунт створено успішно! Тепер можете увійти.');
    router.push('/login');
  } catch (err) {
    // Виводимо помилку від Django (наприклад, "Користувач вже існує")
    const errorMsg = err.response?.data ? JSON.stringify(err.response.data) : 'Помилка реєстрації';
    alert(errorMsg);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-card { max-width: 400px; margin: 50px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
.form-group { margin-bottom: 15px; }
input { width: 100%; padding: 8px; margin-top: 5px; box-sizing: border-box; }
button { width: 100%; padding: 10px; background-color: #42b983; color: white; border: none; cursor: pointer; }
button:disabled { background-color: #ccc; }
.switch-mode { margin-top: 15px; font-size: 0.9em; text-align: center; }
</style>