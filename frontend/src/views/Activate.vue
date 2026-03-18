<template>
  <div class="card shadow">
    <h2>Підтвердження пошти</h2>
    <p v-if="status === 'loading'">Зачекайте, ми перевіряємо ваш токен...</p>
    <div v-if="status === 'success'" class="alert alert-success">
      ✅ {{ message }}
      <router-link to="/login">Перейти до входу</router-link>
    </div>
    <div v-if="status === 'error'" class="alert alert-error">
      ❌ {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const status = ref('loading')
const message = ref('')

onMounted(async () => {
  const { uid, token } = route.params
  try {
    const res = await fetch(`http://localhost:8000/api/accounts/activate/${uid}/${token}/`)
    const data = await res.json()
    
    if (res.ok) {
      status.value = 'success'
      message.value = data.message
    } else {
      status.value = 'error'
      message.value = data.message || 'Помилка активації'
    }
  } catch (e) {
    status.value = 'error'
    message.value = 'Сервер недоступний'
  }
})
</script>

<style scoped>
.card { background: white; padding: 2rem; border-radius: 12px; text-align: center; }
.alert { margin-top: 1rem; padding: 1rem; border-radius: 8px; }
.alert-success { background: #dcfce7; color: #166534; }
.alert-error { background: #fee2e2; color: #991b1b; }
</style>