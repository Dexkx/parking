/**
 * stores/negocios.js
 * Pinia store para la lista y detalle de parqueaderos.
 *
 * Estado:
 *   items   → lista de negocios cargados
 *   loading → estado de carga
 *   error   → error de red
 *
 * Acciones:
 *   fetchNegocios(params) → carga la lista con filtros opcionales
 *   fetchDetalle(nit)     → carga un negocio específico
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { sedesApi } from '@/api/axios'

export const useSedesStore = defineStore('sedes', () => {
  // ── Estado ──────────────────────────────────────
  const items   = ref([])
  const detalle = ref(null)
  const loading = ref(false)
  const error   = ref(null)

  // ── Getters ──────────────────────────────────────
  const disponibles = computed(() => items.value.filter(n => n.status === 'Activo'))
  const total       = computed(() => items.value.length)

  // ── Acciones ──────────────────────────────────────

  /**
   * Obtiene la lista de negocios desde /api/negocios
   * @param {Object} params - Filtros opcionales: search, status, ciudad, etc.
   */
  async function fetchSedes(params = {}) {
    loading.value = true
    error.value   = null
    try {
      const res = await sedesApi.list(params)
      items.value = res.data?.results ?? res.data ?? []
    } catch (e) {
      error.value = 'No se pudieron cargar las sedes.'
      items.value = []
    } finally {
      loading.value = false
    }
  }

  /**
   * Obtiene el detalle de una sede por id
   * @param {string} id
   */
  async function fetchDetalle(nit) {
    loading.value = true
    try {
      const res = await negociosApi.detail(nit)
      detalle.value = res.data
    } catch {
      detalle.value = null
    } finally {
      loading.value = false
    }
  }

  return { items, detalle, loading, error, disponibles, total, fetchSedes, fetchDetalle }
})
