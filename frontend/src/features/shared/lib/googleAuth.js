const GOOGLE_SCRIPT_SRC = 'https://accounts.google.com/gsi/client'

export const loadGoogleScript = () => {
  if (window.google?.accounts?.id) {
    return Promise.resolve()
  }

  return new Promise((resolve, reject) => {
    const existingScript = document.querySelector(`script[src="${GOOGLE_SCRIPT_SRC}"]`)
    if (existingScript) {
      existingScript.addEventListener('load', () => resolve(), { once: true })
      existingScript.addEventListener('error', () => reject(new Error('Google script load failed')), { once: true })
      return
    }

    const script = document.createElement('script')
    script.src = GOOGLE_SCRIPT_SRC
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Google script load failed'))
    document.head.appendChild(script)
  })
}

export const renderGoogleButton = async ({ container, clientId, callback, width = 340 }) => {
  if (!container) {
    throw new Error('Google button container is missing')
  }

  if (!clientId) {
    throw new Error('VITE_GOOGLE_CLIENT_ID is missing')
  }

  await loadGoogleScript()

  window.google.accounts.id.initialize({
    client_id: clientId,
    callback,
  })

  container.innerHTML = ''
  window.google.accounts.id.renderButton(container, {
    type: 'standard',
    theme: 'outline',
    size: 'large',
    shape: 'pill',
    text: 'continue_with',
    width,
    logo_alignment: 'left',
  })
}

