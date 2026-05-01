import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useStorage } from '@vueuse/core'
import { authApi } from '@/api/axios'

export const useAuthStore = defineStore('auth', () => {
  const user = useStorage('p-kab-dashboard-user', null)
  const access = useStorage('p-kab-dashboard-access', null)
  const refresh = useStorage('p-kab-dashboard-refresh', null)
  const loading = ref(true)

  const isAuthenticated = computed(() => !!user.value)
  const userName = computed(() => user.value?.nombre?.split(' ')[0] ?? user.value?.numero_id ?? '')
  const getAccessToken = computed(() => access.value)
  const getRefreshToken = computed(() => refresh.value)

  function setAccessToken(new_token) {
    access.value = new_token
  }

  async function login(numero_id, password) {
    const { data } = await authApi.login({ numero_id, password })
    access.value = data.access
    refresh.value = data.refresh

    const payload = JSON.parse(atob(data.access.split('.')[1]))
    await refreshUser(payload.numero_id)
  }

  const can = (action, entity, item) => {
    if (!user.value || !user.value.roles || !item) return false
    if (user.value.roles.is_superuser) return true


    let role = getRole(entity, item)
    if (!role) return false
    else if (role === "-1") return true // Owner

    // Admin (0)
    if (role === '0') {
      if (action === 'manage_staff') return true
      if ([
        'manage_puestos', 'manage_tarifas',
        'create_puestos', 'create_tarifas',
        'edit_puestos', 'edit_tarifas',
      ].includes(action)
      ) return true

      // Cannot manage the entity itself
      if (['edit', 'delete', 'create'].includes(action) && ['franquicia', 'negocio', 'sede'].includes(entity)) return false
    }

    // Employee (1)
    if (role === '1') {
      if (['view', 'manage_puestos', 'manage_tarifas'].includes(action)) return true

      // if (['create_puestos', 'create_tarifas'].includes(action)) return false
    }

    // Default: allow viewing global entities
    if (action === 'view' && ['cliente', 'reserva'].includes(entity)) return true

    return false
  }

  const getRole = (entity, item) => {
    if (!user.value || !user.value.roles || !item) return null

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
    user.value = userData
  }

  function logout() {
    user.value = null
    access.value = null
    refresh.value = null
  }

  return { user, getAccessToken, getRefreshToken, loading, isAuthenticated, userName, setAccessToken, getRole, login, logout, can, refreshUser }
}, {
  persist: {
    key: 'p-kab-dashboard-auth',
    storage: localStorage,
  },
})
