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
import { search } from '@/api/nominatim'


export function useGeocoder() {
  const geocoding = ref(false)   // true mientras carga
  const error = ref(null)    // mensaje de error si falla

  async function geocodificar(direccion, city, state) {
    if (!direccion?.trim()) return null

    const query = [direccion.trim(), city, state].filter(Boolean).join(', ')

    // Revisar caché
    // if (cache.has(query)) return cache.get(query)

    geocoding.value = true
    error.value     = null

    try {
      const results = await search(query)

      if (!results?.length) {
        error.value = 'No se encontraron coordenadas para esta dirección'
        return []
      }

      return results
    } catch (e) {
      error.value = 'Error al consultar el servicio de mapas.'
      console.error('[useGeocoder]', e)
      return []
    } finally {
      geocoding.value = false
    }
  }

  return { geocodificar, geocoding, error }
}
