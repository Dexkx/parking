/**
 * stores/auth.js
 * Pinia store para manejo de sesión y usuario autenticado.
 *
 * Estado:
 *   user        → datos del usuario (numero_id, nombre)
 *   loading     → cargando sesión inicial
 *
 * Acciones:
 *   login()     → llama /api/token, guarda tokens y decodifica el JWT
 *   logout()    → limpia localStorage y resetea el estado
 *   loadSession → restaura la sesión al recargar la página
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/axios'
import { useRouter } from 'vue-router'
import { useStorage } from '@vueuse/core'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()

  // ── Estado ──────────────────────────────────────
  const user = useStorage('p-kab-user', null)
  const loading = ref(false)

  // Tokens privados pero persistidos automáticamente vía VueUse
  const access = useStorage('p-kab-access', null)
  const refresh = useStorage('p-kab-refresh', null)

  // ── Getters ──────────────────────────────────────
  const getAccessToken = computed(() => access.value)
  const getRefreshToken = computed(() => refresh.value)
  const isAuthenticated = computed(() => !!user.value)
  const userName = computed(() => user.value?.nombre?.split(' ')[0] ?? user.value?.numero_id ?? '')
  const userId = computed(() => user.value?.numero_id)

  // ── Acciones ──────────────────────────────────────

  function setAccessToken(new_token) {
    access.value = new_token
  }

  async function login(numero_id, password) {
    const { data } = await authApi.login({ numero_id, password })

    access.value = data.access
    refresh.value = data.refresh

    const payload = JSON.parse(atob(data.access.split('.')[1]))
    const userData = {
      numero_id: payload.numero_id ?? numero_id,
      nombre: payload.nombre ?? numero_id,
    }

    user.value = userData
  }

  /** Cierra la sesión y limpia todo el almacenamiento local */
  function logout() {
    user.value = null
    access.value = null
    refresh.value = null
    router.push('/')
  }

  return {
    user,
    getAccessToken,
    getRefreshToken,
    loading,
    isAuthenticated,
    userName,
    userId,
    setAccessToken,
    login,
    logout
  }
}, {
  persist: {
    key: 'p-kab-auth',
    storage: localStorage,
  },
})
