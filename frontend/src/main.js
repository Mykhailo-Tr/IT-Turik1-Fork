import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from '@/features/app/AppShell.vue'
import router from '@/features/app/router'
import '@/features/app/styles/base.css'
import 'vue-tel-input/vue-tel-input.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

