import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import Toast, { POSITION } from 'vue-toastification'
import router from '@/router/index.js'
import { useAuthStore } from '@/stores/auth'
import App from './App.vue'
import './assets/main.css'

const app   = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.use(Toast, {
  position: POSITION.BOTTOM_RIGHT,
  timeout: 3500,
  closeOnClick: true,
  pauseOnFocusLoss: false,
  pauseOnHover: true,
  draggable: true,
  hideProgressBar: false,
  maxToasts: 4,
  newestOnTop: true,
})

// Restaurar sesión antes de montar la app
const auth = useAuthStore()
auth.loadSession()

app.mount('#app')
