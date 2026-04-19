/**
 * composables/useGeocoder.js
 *
 * Geocodifica una dirección de texto a coordenadas lat/lng
 * usando la API de Nominatim (OpenStreetMap) — completamente gratuita,
 * sin API key, con límite de 1 request/segundo.
 *
 * Uso:
 *   const { geocodificar, geocoding, error } = useGeocoder()
 *   const coords = await geocodificar('Calle 26 #13-20, Bogotá')
 *   // → { lat: 4.6097, lng: -74.0817 } o null si no encuentra
 */
import { ref } from 'vue'

const NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'

// Caché en memoria para evitar llamadas repetidas
const cache = new Map()

export function useGeocoder() {
  const geocoding = ref(false)   // true mientras carga
  const error     = ref(null)    // mensaje de error si falla

  /**
   * Convierte una dirección en coordenadas.
   * @param {string} direccion - Texto de la dirección
   * @param {string} [ciudad]  - Ciudad o país para afinar la búsqueda
   * @returns {Promise<{lat: number, lng: number} | null>}
   */
  async function geocodificar(direccion, ciudad = 'Colombia') {
    if (!direccion?.trim()) return null

    // Query combinada para mayor precisión
    const query = [direccion.trim(), ciudad.trim()].filter(Boolean).join(', ')

    // Revisar caché
    if (cache.has(query)) return cache.get(query)

    geocoding.value = true
    error.value     = null

    try {
      const params = new URLSearchParams({
        q:              query,
        format:         'json',
        limit:          '1',
        addressdetails: '0',
      })

      const res = await fetch(`${NOMINATIM_URL}?${params}`, {
        headers: {
          // Nominatim requiere User-Agent descriptivo para identificar la app
          'Accept-Language': 'es',
        },
      })

      if (!res.ok) throw new Error(`Nominatim HTTP ${res.status}`)

      const data = await res.json()

      if (!data?.length) {
        error.value = 'No se encontraron coordenadas para esta dirección'
        return null
      }

      const coords = {
        lat: parseFloat(data[0].lat),
        lng: parseFloat(data[0].lon),
      }

      // Guardar en caché
      cache.set(query, coords)
      return coords

    } catch (e) {
      error.value = 'Error al consultar el servicio de mapas. Verifica tu conexión.'
      console.error('[useGeocoder]', e)
      return null
    } finally {
      geocoding.value = false
    }
  }

  return { geocodificar, geocoding, error }
}
