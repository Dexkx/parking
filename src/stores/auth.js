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
    await refreshUser(payload.numero_id)

    return user.value
  }

  const can = (action, entity, item) => {
    if (!user.value || !user.value.roles) return false
    if (user.value.roles.is_superuser) return true

    let role = getRole(entity, item)
    if (!role) return false
    else if(role === "-1") return true // Owner

    // Admin (0)
    if (role === '0') {
      if (action === 'manage_staff') return true
      if (entity === 'sede' && (action === 'manage_puestos' || action === 'manage_tarifas')) return true

      // Cannot manage the entity itself
      if (['edit', 'delete', 'create'].includes(action) && ['franquicia', 'negocio', 'sede'].includes(entity)) return false
    }

    // Employee (1)
    if (role === '1') {
      if (['view'].includes(action)) return true
      return false
    }

    // Default: allow viewing global entities
    if (action === 'view' && ['cliente', 'reserva'].includes(entity)) return true

    return false
  }

  const getRole = (entity, item) => {
    if (!user.value || !user.value.roles) return null

    const id = item.uuid ?? item.nit ?? null;
    if (id == null) return null;

    const role = user.value.roles[entity]?.find(r => r.id === id)?.role || null
    switch (entity) {
      case "sedes":
        return role ? role : getRole('negocios', item.negocio);

      case "negocios":
        return role ? role : getRole('franquicias', item.franquicia);

      case "franquicias":
        return role

      default:
        return null;
    }
  }

  async function refreshUser(numero_id) {
    const { data: userData } = await authApi.me(numero_id)
    localStorage.setItem('user', JSON.stringify(userData))
    user.value = userData
  }

  function logout() {
    localStorage.clear()
    user.value = null
  }

  return { user, loading, isAuthenticated, userName, getRole, loadSession, login, logout, can, refreshUser }
})
