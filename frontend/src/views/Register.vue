<template>
  <div class="card shadow register-container">
    <h2>Реєстрація</h2>
    <p class="subtitle">Створіть акаунт для участі в турнірах</p>

    <div v-if="isSuccess" class="alert alert-success">
      ✅ Реєстрація успішна! Перевірте пошту <strong>{{ form.email }}</strong> для активації акаунту.
    </div>

    <form v-else @submit.prevent="handleRegister">
      <div class="form-grid">
        <div class="form-group">
          <label>Ім'я користувача (ID)</label>
          <input v-model="form.username" type="text" placeholder="johndoe" required />
          <small v-if="errors.username" class="error-msg">{{ errors.username[0] }}</small>
        </div>

        <div class="form-group">
          <label>Електронна пошта</label>
          <input v-model="form.email" type="email" placeholder="example@mail.com" required />
          <small v-if="errors.email" class="error-msg">{{ errors.email[0] }}</small>
        </div>

        <div class="form-group">
          <label>Пароль</label>
          <input v-model="form.password" type="password" placeholder="********" required />
          <small v-if="errors.password" class="error-msg">{{ errors.password[0] }}</small>
        </div>

        <div class="form-group">
          <label>Ваша роль</label>
          <select v-model="form.role" class="custom-select">
            <option value="team">Учасник (Команда)</option>
            <option value="organizer">Організатор</option>
            <option value="jury">Журі</option>
            <option value="admin">Адміністратор</option>
          </select>
        </div>

        <div class="form-group full-width">
          <label>Повне ім'я (ПІБ)</label>
          <input v-model="form.full_name" type="text" placeholder="Іванов Іван Іванович" />
        </div>

        <div class="form-group">
          <label>Телефон</label>
          <input v-model="form.phone" type="text" placeholder="+380XXXXXXXXX" />
          <small v-if="errors.phone" class="error-msg">{{ errors.phone[0] }}</small>
        </div>

        <div class="form-group">
          <label>Місто</label>
          <input v-model="form.city" type="text" placeholder="Київ" />
        </div>
      </div>

      <button type="submit" class="btn-primary" :disabled="isLoading">
        {{ isLoading ? 'Реєстрація...' : 'Зареєструватися' }}
      </button>

      <div class="footer-links">
        Вже маєте акаунт? <router-link to="/login">Увійти</router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const form = ref({
  username: '',
  email: '',
  password: '',
  role: 'team',
  full_name: '',
  phone: '',
  city: ''
})

const errors = ref({})
const isLoading = ref(false)
const isSuccess = ref(false)

const handleRegister = async () => {
  isLoading.value = true
  errors.value = {}

  try {
    const response = await fetch('http://localhost:8000/api/accounts/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(form.value)
    })

    const data = await response.json()

    if (response.ok) {
      isSuccess.value = true
    } else {
      // Записуємо помилки від Django (наприклад, "Користувач з таким іменем вже існує")
      errors.value = data
    }
  } catch (error) {
    alert('Помилка з\'єднання з сервером. Перевірте, чи запущений Django.')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.register-container {
  max-width: 650px;
  margin: 0 auto;
}

h2 { margin-bottom: 0.5rem; text-align: center; color: var(--dark); }
.subtitle { text-align: center; color: #666; margin-bottom: 2rem; }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.2rem;
}

.full-width {
  grid-column: span 2;
}

.form-group {
  display: flex;
  flex-direction: column;
}

label { font-size: 0.9rem; font-weight: 600; margin-bottom: 0.4rem; color: #4b5563; }

input, select {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
}

input:focus, select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.custom-select {
  cursor: pointer;
}

.btn-primary {
  grid-column: span 2;
  margin-top: 1.5rem;
  padding: 0.8rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  width: 100%;
}

.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }

.error-msg { color: #ef4444; font-size: 0.8rem; margin-top: 0.3rem; }

.alert {
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  line-height: 1.5;
}
.alert-success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }

.footer-links {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.95rem;
  color: #666;
}

/* Адаптивність для телефонів */
@media (max-width: 600px) {
  .form-grid { grid-template-columns: 1fr; }
  .full-width { grid-column: span 1; }
  .btn-primary { grid-column: span 1; }
}
</style>