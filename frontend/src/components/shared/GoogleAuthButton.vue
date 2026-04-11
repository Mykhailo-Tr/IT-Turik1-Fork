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
import { renderGoogleButton, type GoogleCredentialResponse } from '@/lib/googleAuth'
import { useGoogleLogin } from '@/queries/accounts'

interface Props {
  dividerLabel?: string
  buttonWidth?: number
}

const props = withDefaults(defineProps<Props>(), {
  dividerLabel: 'or continue with',
  buttonWidth: 340,
})

const emit = defineEmits(['success'])

const googleButtonRef = ref<HTMLDivElement | null>(null)
const errorMessage = ref('')
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

const { mutate: googleLogin } = useGoogleLogin()

const handleGoogleCredential = (response: GoogleCredentialResponse) => {
  if (!response?.credential) {
    errorMessage.value = 'Google did not return a credential token.'
    return
  }

  errorMessage.value = ''

  googleLogin(
    { body: { credential: response.credential } },
    {
      onSuccess: (data) => {
        emit('success', data)
      },
      onError: (err) => {
        errorMessage.value = err.response
          ? 'Google authentication failed.'
          : 'Network error during Google authentication.'
      },
    },
  )
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
