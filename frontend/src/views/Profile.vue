<template>
  <div class="card shadow profile-container">
    <h2>Мій профіль</h2>
    <hr />

    <div v-if="notification" :class="['alert', notification.type]">
      {{ notification.message }}
    </div>

    <form @submit.prevent="handleUpdate">
      <div class="info-grid">
        <div class="info-item">
          <label>Логін:</label>
          <span>{{ profile.username }}</span>
        </div>
        <div class="info-item">
          <label>Email:</label>
          <span>{{ profile.email }}</span>
        </div>
        <div class="info-item">
          <label>Роль:</label>
          <span class="badge">{{ profile.role }}</span>
        </div>
      </div>

      <div class="form-group">
        <label for="full_name">Повне ім'я</label>
        <input id="full_name" v-model="form.full_name" type="text" placeholder="ПІБ" />
      </div>

      <div class="form-group">
        <label for="phone">Телефон</label>
        <input id="phone" v-model="form.phone" type="text" placeholder="+380..." />
        <p v-if="errors.phone" class="error-msg">{{ errors.phone[0] }}</p>
      </div>

      <div class="form-group">
        <label for="city">Місто</label>
        <input id="city" v-model="form.city" type="text" placeholder="Ваше місто" />
      </div>

      <button type="submit" class="btn-primary" :disabled="loading">
        {{ loading ? 'Збереження...' : 'Оновити дані' }}
      </button>
    </form>
    
    <p class="meta">Дата реєстрації: {{ formatDate(profile.created_at) }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const profile = ref({})
const form = ref({ full_name: '', phone: '', city: '' })
const loading = ref(false)
const errors = ref({})
const notification = ref(null)

const fetchProfile = async () => {
  const token = localStorage.getItem('access')
  const res = await fetch('http://localhost:8000/api/accounts/profile/', {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (res.ok) {
    const data = await res.json()
    profile.value = data
    form.value = { 
      full_name: data.full_name || '', 
      phone: data.phone || '', 
      city: data.city || '' 
    }
  }
}

const handleUpdate = async () => {
  loading.value = true
  errors.value = {}
  notification.value = null
  
  const token = localStorage.getItem('access')
  try {
    const res = await fetch('http://localhost:8000/api/accounts/profile/', {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form.value)
    })

    const data = await res.json()
    if (res.ok) {
      notification.value = { type: 'success', message: 'Дані успішно оновлено!' }
      profile.value = { ...profile.value, ...data }
    } else {
      errors.value = data
      notification.value = { type: 'error', message: 'Помилка валідації.' }
    }
  } catch (err) {
    notification.value = { type: 'error', message: 'Помилка з\'єднання з сервером.' }
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('uk-UA')
}

onMounted(fetchProfile)
</script>

<style scoped>
.profile-container { max-width: 600px; margin: 2rem auto; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem; background: #f8f9fa; padding: 1rem; border-radius: 8px; }
.info-item label { font-size: 0.85rem; color: #666; display: block; }
.info-item span { font-weight: bold; }
.badge { background: #e9ecef; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; font-size: 0.75rem; }
.meta { margin-top: 1.5rem; font-size: 0.8rem; color: #999; text-align: center; }
.error-msg { color: #dc3545; font-size: 0.8rem; margin: 0.2rem 0; }
.btn-primary { width: 100%; padding: 0.8rem; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
.btn-primary:hover { background: #0056b3; }
.btn-primary:disabled { background: #ccc; }
.alert { padding: 1rem; border-radius: 5px; margin-bottom: 1rem; text-align: center; }
.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
</style>