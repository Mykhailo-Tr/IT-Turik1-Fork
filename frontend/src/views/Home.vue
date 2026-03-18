<template>
  <div class="home-container">
    <header class="navbar">
      <h2>Платформа Турнірів</h2>
      <button @click="handleLogout" class="logout-btn">Вийти</button>
    </header>

    <main class="content">
      <h3>Вітаємо в системі!</h3>
      
      <div v-if="isLoading" class="loading">Завантаження профілю...</div>
      
      <div v-else-if="error" class="error">{{ error }}</div>
      
      <div v-else-if="userProfile" class="profile-card">
        <p><strong>Ім'я користувача:</strong> {{ userProfile.username }}</p>
        <p><strong>Email:</strong> {{ userProfile.email }}</p>
        <p><strong>Роль:</strong> {{ userProfile.role }}</p>
        <p v-if="userProfile.team"><strong>Команда:</strong> {{ userProfile.team }}</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// Створюємо реактивні змінні для збереження стану компонента
const userProfile = ref(null)
const isLoading = ref(true)
const error = ref('')
const router = useRouter()

// onMounted виконується одразу після того, як компонент з'являється на екрані
onMounted(async () => {
  // Дістаємо токен доступу зі сховища браузера
  const token = localStorage.getItem('access')
  
  try {
    // Робимо запит до захищеного ендпоінту, який ми створили в Django (UserProfileView)
    const response = await fetch('http://localhost:8000/api/accounts/profile/', {
      method: 'GET',
      headers: {
        // Чому так: DRF SimpleJWT очікує заголовок Authorization у форматі "Bearer <token>"
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    if (response.ok) {
      // Якщо запит успішний, розпаршуємо JSON і зберігаємо в реактивну змінну
      userProfile.value = await response.json()
    } else {
      // Якщо токен прострочений або недійсний (статус 401 Unauthorized)
      if (response.status === 401) {
         handleLogout() // Автоматично розлогінюємо користувача
      } else {
         error.value = 'Не вдалося завантажити дані профілю.'
      }
    }
  } catch (err) {
    error.value = 'Помилка з\'єднання з сервером. Перевір, чи запущений Django.'
  } finally {
    // Вимикаємо індикатор завантаження у будь-якому випадку
    isLoading.value = false
  }
})

// Логіка виходу з акаунту
const handleLogout = () => {
  // Чому так: Щоб вийти, достатньо просто видалити токени з localStorage браузера.
  // Після цього Navigation Guard (у router/index.js) більше не пустить нас на захищені сторінки.
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  
  // Перекидаємо користувача на сторінку логіну
  router.push('/login')
}
</script>

<style scoped>
/* Чистий CSS для головної сторінки */
.home-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #343a40;
  color: white;
  padding: 1rem 2rem;
}

.navbar h2 {
  margin: 0;
  font-size: 1.5rem;
}

.logout-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.logout-btn:hover {
  background-color: #c82333;
}

.content {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.loading {
  font-size: 1.2rem;
  color: #666;
}

.error {
  color: #dc3545;
  background-color: #f8d7da;
  padding: 1rem;
  border-radius: 4px;
  border: 1px solid #f5c6cb;
}

.profile-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-top: 1rem;
}

.profile-card p {
  margin: 0.5rem 0;
  font-size: 1.1rem;
}
</style>