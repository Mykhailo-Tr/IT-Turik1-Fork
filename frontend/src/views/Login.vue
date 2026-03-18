<template>
  <div class="auth-container">
    <form @submit.prevent="handleLogin" class="auth-form">
      <h2>Вхід</h2>
      
      <div class="form-group">
        <label>Ім'я користувача</label>
        <input v-model="form.username" type="text" required />
      </div>

      <div class="form-group">
        <label>Пароль</label>
        <input v-model="form.password" type="password" required />
      </div>

      <button type="submit" :disabled="isLoading">Увійти</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const form = ref({ username: '', password: '' })
const error = ref('')
const isLoading = ref(false)
const router = useRouter()

const handleLogin = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    const response = await fetch('http://localhost:8000/api/accounts/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    
    const data = await response.json()
    
    if (response.ok) {
      // Як працює збереження: 
      // localStorage - це API браузера, що дозволяє зберігати дані у вигляді ключ-значення без терміну дії.
      // Зберігаємо access для запитів і refresh для оновлення токена.
      localStorage.setItem('access', data.access)
      localStorage.setItem('refresh', data.refresh)
      
      // Перенаправляємо на захищену сторінку
      router.push('/')
    } else {
      error.value = 'Невірний логін, пароль, або акаунт не активовано.'
    }
  } catch (err) {
    error.value = 'Помилка мережі'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* Використовуємо ті ж базові стилі, що і в Register.vue */
.auth-container { display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f4f4f9; }
.auth-form { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
.form-group { margin-bottom: 1rem; }
input { width: 100%; padding: 0.5rem; margin-top: 0.5rem; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
button { width: 100%; padding: 0.75rem; background-color: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; }
.error { color: #dc3545; margin-top: 1rem; text-align: center; }
</style>