<template>
  <div class="transition-wrapper">
    <!-- ─── Hero ─────────────────────────────── -->
    <section class="grid grid-cols-2 overflow-hidden" style="height:calc(100vh - 64px)">

      <!-- Izquierda: copy y búsqueda -->
      <div class="flex flex-col justify-center px-12 lg:px-20 py-16 relative z-10 animate-fade-up">

        <!-- Eyebrow chip -->
        <div
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold text-accent w-fit mb-6"
          style="background:rgba(0,229,176,0.1);border:1px solid rgba(0,229,176,0.25)">
          <Star :size="11" fill="currentColor" />
          La plataforma #1 de parqueaderos en Colombia
        </div>

        <!-- Título -->
        <h1 class="font-head font-extrabold leading-[1.04] tracking-tight text-t-primary mb-5"
          style="font-size:clamp(38px,5vw,60px)">
          Tu parqueadero<br>
          <span class="text-accent">perfecto,</span><br>
          en segundos.
        </h1>

        <!-- Subtítulo -->
        <p class="text-t-secondary text-base leading-relaxed max-w-md mb-10">
          Encuentra, reserva y paga tu espacio de parqueo desde la app.
          Sin filas. Sin complicaciones.
        </p>

        <!-- Barra de búsqueda -->
        <form class="flex items-center gap-2 bg-card border border-border rounded-lg px-4 py-1.5 max-w-md"
          @submit.prevent="buscar">
          <Search :size="15" class="text-t-muted shrink-0" />
          <input v-model="query"
            class="flex-1 bg-transparent border-none outline-none text-t-primary text-sm placeholder:text-t-muted font-body py-1.5"
            placeholder="Ciudad, barrio o nombre del parqueadero..." />
          <button type="submit" class="btn-primary text-sm px-4 py-2 shrink-0">
            <Search :size="13" /> Buscar
          </button>
        </form>

        <!-- Stats -->
        <div class="flex gap-10 mt-10">
          <div v-for="s in [
            { num: store.total > 0 ? store.total + '+' : '150+', label: 'Parqueaderos' },
            { num: '12K+', label: 'Usuarios activos' },
            { num: '4.8★', label: 'Valoración media' },
          ]" :key="s.label" class="flex flex-col gap-0.5">
            <span class="font-head font-extrabold text-3xl tracking-tight text-t-primary">{{ s.num }}</span>
            <span class="text-xs text-t-muted font-medium">{{ s.label }}</span>
          </div>
        </div>
      </div>

      <!-- Derecha: Mapa -->
      <div class="relative">
        <!-- Gradiente de transición izquierda → mapa -->
        <div class="absolute left-0 top-0 bottom-0 w-20 z-10 pointer-events-none"
          style="background:linear-gradient(to right, #080a0f, transparent)" />
        <MapView :negocios="store.items" class="h-full" />
      </div>
    </section>

    <!-- ─── Features ─────────────────────────── -->
    <section class="bg-surface border-t border-border px-12 lg:px-20 py-20">
      <div class="max-w-screen-xl mx-auto">

        <p class="text-xs text-accent font-semibold tracking-widest uppercase mb-3">¿Por qué ParkApp?</p>
        <h2 class="font-head font-extrabold text-4xl tracking-tight text-t-primary mb-2">
          Todo lo que necesitas
        </h2>
        <p class="text-t-secondary text-base max-w-md">
          Diseñado para conductores colombianos que valoran su tiempo y su dinero.
        </p>

        <!-- Grid de features -->
        <div class="grid grid-cols-3 gap-5 mt-12">
          <div v-for="(f, i) in features" :key="f.title"
            class="card-dark rounded-lg p-6 hover:-translate-y-1 transition-all duration-200 animate-fade-up"
            :style="{ animationDelay: `${i * 100}ms` }">
            <!-- Icono -->
            <div :class="['w-11 h-11 rounded-sm flex items-center justify-center mb-4', f.bg, f.color]">
              <component :is="f.icon" :size="20" />
            </div>
            <h3 class="font-head font-bold text-base text-t-primary mb-2">{{ f.title }}</h3>
            <p class="text-sm text-t-secondary leading-relaxed">{{ f.desc }}</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
/**
 * HomePage.vue
 * Página principal con:
 *  - Hero split: copy + barra de búsqueda a la izquierda / Mapa a la derecha
 *  - Sección de características (features)
 *  - Stats dinámicos desde el store
 */
import { ref, onMounted, Fragment } from 'vue'
import { useRouter } from 'vue-router'
import { Search, MapPin, Zap, Shield, Star } from 'lucide-vue-next'
import MapView from '@/components/MapView.vue'
import { useSedesStore } from '@/stores/sedes'

const router = useRouter()
const store = useSedesStore()
const query = ref('')

onMounted(() => store.fetchSedes())

const features = [
  {
    icon: MapPin, color: 'text-accent', bg: 'bg-accent/10',
    title: 'Mapa en tiempo real',
    desc: 'Visualiza todos los parqueaderos disponibles en tu ciudad con información actualizada.',
  },
  {
    icon: Zap, color: 'text-blue', bg: 'bg-blue/10',
    title: 'Reserva en segundos',
    desc: 'Selecciona tu espacio, elige la duración y confirma. Tu puesto queda asegurado.',
  },
  {
    icon: Shield, color: 'text-warn', bg: 'bg-warn/10',
    title: 'Pago seguro',
    desc: 'Múltiples métodos de pago. Efectivo, tarjeta o transferencia. Tú decides.',
  },
]

function buscar() {
  router.push({ name: 'resultados', query: { q: query.value } })
}
</script>
