import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/axios'

export const useAuthStore = defineStore('auth', () => {
  const user    = ref(null)
  const loading = ref(true)

  const isAuthenticated = computed(() => !!user.value)
  const userName = computed(() => user.value?.nombre?.split(' ')[0] ?? user.value?.numero_id ?? '')

  function loadSession() {
    const stored = localStorage.getItem('user')
    if (stored) user.value = JSON.parse(stored)
    loading.value = false
  }

  async function login(numero_id, password) {
    const { data } = await authApi.login({ numero_id, password })
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    const payload = JSON.parse(atob(data.access.split('.')[1]))
    const userData = { numero_id: payload.numero_id ?? numero_id, nombre: payload.nombre ?? numero_id }
    localStorage.setItem('user', JSON.stringify(userData))
    user.value = userData
    return userData
  }

  function logout() {
    localStorage.clear()
    user.value = null
  }

  return { user, loading, isAuthenticated, userName, loadSession, login, logout }
})
