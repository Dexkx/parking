<template>
  <div class="h-full w-full rounded-lg overflow-hidden">
    <LMap
      ref="mapRef"
      :zoom="12"
      :center="mapCenter"
      :use-global-leaflet="false"
      style="height:100%;width:100%"
    >
      <!-- Tiles de OpenStreetMap (se oscurece via CSS global) -->
      <LTileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap"
      />

      <!-- Marcadores de parqueaderos -->
      <LMarker
        v-for="neg in markersConPos"
        :key="neg.nit"
        :lat-lng="[neg._lat, neg._lng]"
        :icon="createIcon(neg.status === 'Activo')"
      >
        <LPopup>
          <div class="font-body min-w-[170px] p-1">
            <p class="font-head font-bold text-sm text-t-secondary mb-1">{{ neg.nombre }}</p>
            <p class="text-xs text-t-secondary mb-2.5">{{ neg.direccion }}</p>
            <div class="flex justify-between items-center text-xs">
              <span class="text-accent font-semibold">
                {{ formatPrecio(neg.tarifas?.[0]?.valor) }}
              </span>
              <span class="flex items-center gap-1 text-t-secondary">
                <Star :size="10" fill="#fbbf24" color="#fbbf24" />
                {{ neg.puntuacion ? Number(neg.puntuacion).toFixed(1) : '—' }}
              </span>
            </div>
          </div>
        </LPopup>
      </LMarker>

      <LMarker
        v-if="userLocation"
        :key="'ubicacion'"
        :lat-lng="userLocation"
        :icon="userLocationIcon"
      >
        <LPopup>
          <div class="font-body min-w-[170px] p-1">
            <p class="font-head font-bold text-sm text-t-secondary mb-1">Mi ubicación</p>
            <p class="text-xs text-t-secondary mb-2.5">Estás aquí</p>
          </div>
        </LPopup>
      </LMarker>

    </LMap>
  </div>
</template>

<script setup>
/**
 * MapView.vue
 * Mapa interactivo usando @vue-leaflet/vue-leaflet.
 *
 * Props:
 *   negocios → lista de parqueaderos para mostrar como marcadores
 *   center   → [lat, lng] centro del mapa
 */
import { computed, h, onBeforeMount, reactive, ref, render } from 'vue'
import { LMap, LTileLayer, LMarker, LPopup, LGeoJson } from '@vue-leaflet/vue-leaflet'
import L from 'leaflet'
import { MapPinHouse, Star } from 'lucide-vue-next'

const props = defineProps({
  negocios: { type: Array, default: () => [] },
})


// Ref para el mapa (esto es correcto)
const mapRef = ref(null)

// Centro del mapa (usando ref, no reactive)
const mapCenter = ref([4.711, -74.072])

// Ubicación del usuario (null si no se ha obtenido)
const userLocation = ref(null)


onBeforeMount(() => {
  if (!navigator.geolocation) {
    alert("Tu navegador no soporta geolocalización.")
    return
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude } = position.coords
      // Guardar ubicación del usuario
      userLocation.value = [latitude, longitude]

      // Mover el centro del mapa
      mapCenter.value = [latitude, longitude]

      // Animar el mapa si está disponible
      if (mapRef.value && mapRef.value.leafletObject) {
        mapRef.value.leafletObject.flyTo([latitude, longitude], 15)
      }
    },
    (error) => {
      console.error("Error obteniendo ubicación:", error)
      alert("No se pudo obtener tu ubicación.")
    }
  )
})

// Icono especial para la ubicación del usuario
const userLocationIcon = L.divIcon({
  className: '',
  html: contentUserLocationIcon(),
  iconSize: [34, 34],
  iconAnchor: [17, 34],
  popupAnchor: [0, -38],
})
function contentUserLocationIcon () {
  const rendering =
      h(MapPinHouse, { size: 40, fill: '#D64700', color: '#fff', strokeWidth: 1 })

  const container = document.createElement('div')
  render(rendering, container)
  return container.innerHTML
}

// Icono custom HTML por disponibilidad
const createIcon = (disponible) => L.divIcon({
  className: '',
  html: `
    <div
      class="flex items-center justify-center border-2 border-${disponible ? 'white' : '[#2a2d38]'} size-8 -rotate-45 shadow-[0_4px_14px_rgba(0,0,0,0.5)]
        rounded-[50%_50%_50%_0] bg-[--card]"
      style="--card: ${disponible ? '#00e5b0' : '#4e5568'};">
      <span
        class="text-white font-head font-bold text-sm rotate-45 text-[--color]"
        style="--color: ${disponible ? '#000' : '#aaa'};">P</span>
    </div>`,
  iconSize:   [34, 34],
  iconAnchor: [17, 34],
  popupAnchor:[0, -38],
})

// Posición simulada si el negocio no tiene lat/lng
const markersConPos = computed(() => props.negocios.map(n => ({
  ...n,
  _lat: n.lat ?? (4.711 + (Math.random() - 0.5) * 0.06),
  _lng: n.lng ?? (-74.072 + (Math.random() - 0.5) * 0.06),
})))

const formatPrecio = (val) => val
  ? `$${Number(val).toLocaleString('es-CO')}/h`
  : 'Ver tarifas'
</script>
