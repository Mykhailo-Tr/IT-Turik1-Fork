<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const message = ref('Завантаження...')

onMounted(async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/hello/')
    message.value = response.data.message
  } catch (error) {
    console.error("Помилка:", error)
    message.value = "Не вдалося отримати дані."
  }
})
</script>

<template>
  <div style="text-align: center; margin-top: 50px;">
    <h1>Результат з бекенду:</h1>
    <p style="font-size: 24px; color: green;">{{ message }}</p>
  </div>
</template>