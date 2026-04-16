<template>
  <!-- Layout split: sidebar lista + mapa -->
  <div class="flex overflow-hidden" style="height:calc(100vh - 64px)">

    <!-- ─── Sidebar ─────────────── -->
    <aside class="w-[400px] shrink-0 flex flex-col border-r border-border overflow-hidden">

      <!-- Cabecera del sidebar -->
      <div class="px-4 pt-4 pb-3 border-b border-border">
        <h1 class="font-head font-bold text-lg text-t-primary mb-3">Parqueaderos</h1>

        <!-- Buscador -->
        <div class="flex items-center gap-2 bg-input border border-border rounded-sm px-3 py-2">
          <Search :size="13" class="text-t-muted shrink-0" />
          <input
            v-model="query"
            class="flex-1 bg-transparent border-none outline-none text-sm text-t-primary placeholder:text-t-muted font-body"
            placeholder="Buscar por nombre o dirección..."
          />
          <Loader2 v-if="store.loading" :size="13" class="text-t-muted animate-spin-slow shrink-0" />
        </div>
      </div>

      <!-- Chips de filtro -->
      <div class="flex gap-2 px-4 py-2.5 border-b border-border overflow-x-auto">
        <button
          v-for="f in FILTROS"
          :key="f.key"
          :class="['filter-chip', filtroActivo === f.key ? 'filter-chip-active' : 'filter-chip-inactive']"
          @click="filtroActivo = f.key"
        >
          {{ f.label }}
        </button>
      </div>

      <!-- Contador de resultados -->
      <div class="px-4 py-2 text-xs text-t-muted">
        {{ negociosFiltrados.length }} resultado{{ negociosFiltrados.length !== 1 ? 's' : '' }}
      </div>

      <!-- Lista de tarjetas -->
      <div class="flex-1 overflow-y-auto px-3 pb-4">

        <!-- Skeleton de carga -->
        <template v-if="store.loading">
          <div v-for="i in 4" :key="i" class="skeleton h-44 mb-3" />
        </template>

        <!-- Estado vacío -->
        <div v-else-if="negociosFiltrados.length === 0"
             class="flex flex-col items-center justify-center gap-3 text-t-muted">
          <SlidersHorizontal :size="36" :stroke-width="1" />
          <p class="font-head font-bold">Sin resultados</p>
          <p class="text-xs text-center max-w-[200px]">
            Intenta con otra búsqueda o elimina los filtros
          </p>
        </div>

        <!-- Tarjetas -->
        <template v-else>
          <div class="flex flex-col gap-3 pt-1">
            <ParkCard
              v-for="(neg, i) in negociosFiltrados"
              :key="neg.nit"
              :negocio="neg"
              :index="i"
              @login-required="$emit('login-required')"
            />
          </div>
        </template>
      </div>
    </aside>

    <!-- ─── Mapa ─────────────────── -->
    <div class="flex-1">
      <MapView :negocios="negociosFiltrados" class="h-full" />
    </div>
  </div>
</template>

<script setup>
/**
 * ResultadosPage.vue
 * Página de resultados con sidebar de tarjetas y mapa lateral.
 *
 * Filtros disponibles:
 *   - Búsqueda por texto
 *   - Solo disponibles
 *   - Mejor valorados
 *
 * Datos:
 *   - Se obtienen del store de negocios con parámetros de filtro
 */
import { ref, watch, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Search, Loader2, SlidersHorizontal } from 'lucide-vue-next'
import ParkCard from '@/components/ParkCard.vue'
import MapView from '@/components/MapView.vue'
import { useNegociosStore } from '@/stores/negocios'

const emit  = defineEmits(['login-required'])
const route = useRoute()
const store = useNegociosStore()

// ── Filtros ────────────────────────────────────────
const query       = ref(route.query.q ?? '')
const filtroActivo = ref('all')  // 'all' | 'disponible' | 'mejor_valorado'

const FILTROS = [
  { key: 'all',           label: 'Todos' },
  { key: 'disponible',    label: 'Disponibles' },
  { key: 'mejor_valorado', label: 'Mejor valorados' },
]

// Computar la lista según el filtro activo
const negociosFiltrados = computed(() => {
  let lista = [...store.items]
  if (filtroActivo.value === 'disponible')
    lista = lista.filter(n => n.status === 'Activo')
  if (filtroActivo.value === 'mejor_valorado')
    lista = lista.sort((a, b) => (b.puntuacion ?? 0) - (a.puntuacion ?? 0))
  return lista
})

// Cargar datos cuando cambia la búsqueda (debounce manual con watch)
let searchTimeout = null
watch(query, (val) => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => cargar(val), 350)
})

onMounted(() => cargar(query.value))

async function cargar(q = '') {
  const params = {}
  if (q) params.search = q
  await store.fetchNegocios(params)
}
</script>

