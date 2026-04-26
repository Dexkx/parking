/**
 * main.js — Punto de entrada de la aplicación
 *
 * Registra todos los plugins en orden:
 *  1. Pinia  → manejo de estado global (auth, negocios)
 *  2. Router → navegación con guards
 *  3. Toast  → notificaciones
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import Toast, { POSITION } from 'vue-toastification'
import router from '@/router/index.js'
import App from './App.vue'
import './assets/main.css'

const app   = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.use(Toast, {
  position: POSITION.BOTTOM_RIGHT,
  timeout:  3500,
  closeOnClick: true,
  pauseOnFocusLoss: false,
  pauseOnHover: true,
  draggable: true,
  hideProgressBar: false,
  transition: 'Vue-Toastification__fade',
  maxToasts: 4,
  newestOnTop: true,
})

app.mount('#app')
