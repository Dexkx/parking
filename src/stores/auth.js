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

export const useAuthStore = defineStore('auth', () => {
  // ── Estado ──────────────────────────────────────
  const user    = ref(null)
  const loading = ref(true)

  // ── Getters ──────────────────────────────────────
  const isAuthenticated = computed(() => !!user.value)
  const userName = computed(() => user.value?.nombre?.split(' ')[0] ?? user.value?.numero_id ?? '')
  const userId = computed(() => user.value?.numero_id)

  // ── Acciones ──────────────────────────────────────

  /** Restaura la sesión guardada en localStorage */
  function loadSession() {
    const stored = localStorage.getItem('user')
    if (stored) user.value = JSON.parse(stored)
    loading.value = false
  }

  /**
   * Inicia sesión con número de identificación y contraseña.
   * Guarda access_token, refresh_token y datos del usuario.
   */
  async function login(numero_id, password) {
    const { data } = await authApi.login({ numero_id, password })

    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)

    // Decodificar payload del JWT para obtener datos del usuario
    const payload = JSON.parse(atob(data.access.split('.')[1]))
    const userData = {
      numero_id: payload.numero_id ?? numero_id,
      nombre:    payload.nombre    ?? numero_id,
    }

    localStorage.setItem('user', JSON.stringify(userData))
    user.value = userData
    return userData
  }

  /** Cierra la sesión y limpia todo el almacenamiento local */
  function logout() {
    localStorage.clear()
    user.value = null
  }

  return { user, loading, isAuthenticated, userName, userId, loadSession, login, logout }
}, {
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'p-kab-auth',
        storage: localStorage,
      },
    ],
  },
})
