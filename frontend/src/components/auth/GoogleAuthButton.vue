<template>
  <div class="google-auth">
    <div v-if="dividerLabel" class="divider-line"><span>{{ dividerLabel }}</span></div>
    <div ref="googleButtonRef" class="google-slot"></div>
    <p v-if="errorMessage" class="text-error text-center feedback">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

import { renderGoogleButton } from '@/utils/googleAuth'

import { API_BASE } from '@/config/api'

const props = defineProps({
  apiBase: {
    type: String,
    default: API_BASE,
  },
  dividerLabel: {
    type: String,
    default: 'or continue with',
  },
  buttonWidth: {
    type: Number,
    default: 340,
  },
})

const emit = defineEmits(['success'])

const googleButtonRef = ref(null)
const errorMessage = ref('')
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

const handleGoogleCredential = async (response) => {
  if (!response?.credential) {
    errorMessage.value = 'Google did not return a credential token.'
    return
  }

  errorMessage.value = ''

  try {
    const backendResponse = await fetch(`${props.apiBase}/api/accounts/google-login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ credential: response.credential }),
    })

    const data = await backendResponse.json()

    if (backendResponse.ok) {
      emit('success', data)
      return
    }

    errorMessage.value = data.detail || 'Google authentication failed.'
  } catch {
    errorMessage.value = 'Network error during Google authentication.'
  }
}

onMounted(async () => {
  try {
    await renderGoogleButton({
      container: googleButtonRef.value,
      clientId: googleClientId,
      callback: handleGoogleCredential,
      width: props.buttonWidth,
    })
  } catch (error) {
    errorMessage.value = error.message || 'Google auth initialization failed.'
  }
})
</script>

<style scoped>
.feedback {
  margin-top: 0.6rem;
}
</style>
