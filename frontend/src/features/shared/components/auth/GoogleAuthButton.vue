<template>
  <div class="google-auth">
    <div v-if="dividerLabel" class="divider-line">
      <span>{{ dividerLabel }}</span>
    </div>
    <div ref="googleButtonRef" class="google-slot"></div>
    <p v-if="errorMessage" class="text-error text-center feedback">{{ errorMessage }}</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { renderGoogleButton, type GoogleCredentialResponse } from '@/features/shared/lib/googleAuth'
import { API_BASE } from '@/features/shared/config/api'
import $api from '@/services'
import { isApiError } from '@/services/apiClient'

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

const googleButtonRef = ref<HTMLDivElement | null>(null)
const errorMessage = ref('')
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

const handleGoogleCredential = async (response: GoogleCredentialResponse) => {
  if (!response?.credential) {
    errorMessage.value = 'Google did not return a credential token.'
    return
  }

  errorMessage.value = ''

  try {
    const backendResponse = await $api.accounts.googleLogin({ credential: response.credential })

    emit('success', backendResponse.data)
  } catch (err) {
    if (isApiError(err)) {
      if (err.response) {
        errorMessage.value = err.response.data.detail || 'Google authentication failed.'
      } else {
        errorMessage.value = 'Network error during Google authentication.'
      }
    }
  }
}

onMounted(async () => {
  try {
    if (!googleButtonRef.value) throw new Error('container is not mounted')

    await renderGoogleButton({
      container: googleButtonRef.value,
      clientId: googleClientId,
      callback: handleGoogleCredential,
      width: props.buttonWidth,
    })
  } catch (error) {
    errorMessage.value =
      (error instanceof Error && error.message) || 'Google auth initialization failed.'
  }
})
</script>

<style scoped>
.feedback {
  margin-top: 0.6rem;
}
</style>
