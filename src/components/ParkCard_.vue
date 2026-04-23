<template>
  <article
    class="card-dark rounded-lg overflow-hidden hover:-translate-y-1 hover:shadow-card transition-all duration-200 cursor-pointer animate-fade-up"
    :style="{ animationDelay: animDelay }"
  >
    <!-- Cabecera: nombre + badge disponibilidad -->
    <div class="flex justify-between items-start p-4 pb-0">
      <div class="flex-1 min-w-0 pr-3">
        <h3 class="font-head font-bold text-[15px] leading-tight text-t-primary truncate">
          {{ sede.nombre }}
        </h3>
        <p class="flex items-center gap-1 text-xs text-t-secondary mt-1">
          <MapPin :size="10" class="text-accent shrink-0" />
          <span class="truncate">{{ sede.direccion }}</span>
        </p>
      </div>

      <!-- Badge de disponibilidad -->
      <span :class="disponible ? 'badge-green' : 'badge-red'" class="shrink-0">
        <span :class="['w-1.5 h-1.5 rounded-full', disponible ? 'animate-pulse-dot bg-accent' : 'bg-danger']" />
        {{ disponible ? 'Disponible' : 'Cerrado' }}
      </span>
    </div>

    <!-- Separador -->
    <div class="h-px bg-border mx-4 my-3" />

    <!-- Stats en grid 3 columnas -->
    <div class="grid grid-cols-3 gap-2 px-4">
      <div class="bg-input rounded-sm p-2.5">
        <div class="text-[10px] text-t-muted font-medium tracking-wider uppercase mb-1">Precio/hora</div>
        <div class="font-head font-bold text-t-primary text-base text-accent">{{ precioBase }}</div>
      </div>
      <div class="bg-input rounded-sm p-2.5">
        <div class="text-[10px] text-t-muted font-medium tracking-wider uppercase mb-1">Puestos</div>
        <div class="font-head font-bold text-base text-t-primary">{{ sede.puestos_count ?? '—' }}</div>
      </div>
      <div class="bg-input rounded-sm p-2.5">
        <div class="text-[10px] text-t-muted font-medium tracking-wider uppercase mb-1">Ciudad</div>
        <div class="text-sm font-medium text-t-secondary truncate">{{ sede.city?.name ?? '—' }}</div>
      </div>
    </div>

    <!-- Footer: estrellas + botón reservar -->
    <div class="flex justify-between items-center px-4 py-3 mt-1">
      <!-- Estrellas -->
      <div class="flex items-center gap-1">
        <Star v-for="n in 5" :key="n"
              :size="12"
              :fill="n <= estrellas ? '#fbbf24' : 'none'"
              :color="n <= estrellas ? '#fbbf24' : '#4e5568'"
              :stroke-width="1.5" />
        <span class="text-xs text-t-secondary ml-1">
          {{ puntuacion > 0 ? puntuacion.toFixed(1) : '—' }}
        </span>
      </div>

      <!-- Btn reservar -->
      <button class="btn-primary text-xs px-3 py-1.5" @click="reservar">
        Reservar <ChevronRight :size="13" />
      </button>
    </div>
  </article>
</template>

<script setup>
/**
 * ParkCard.vue
 * Tarjeta para mostrar un parqueadero en la lista de resultados.
 *
 * Props:
 *   negocio  → objeto del negocio/parqueadero
 *   index    → posición en la lista (para el delay de animación)
 *
 * Emits:
 *   login-required → si el usuario intenta reservar sin sesión
 */
import { computed } from 'vue'
import { MapPin, Star, ChevronRight } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { reservasApi } from '@/api/axios'
import { useSwal } from '@/composables/useSwal'
import { useToast } from 'vue-toastification'

const props = defineProps({
  sede: { type: Object, required: true },
  index:   { type: Number, default: 0 },
})
const emit = defineEmits(['login-required'])

const auth  = useAuthStore()
const toast = useToast()
const { promptReserva } = useSwal()

// ── Computed ──────────────────────────────
const disponible  = computed(() => props.sede.status === 'Activo')
const precioBase  = computed(() => props.sede.tarifas?.[0]?.valor
  ? `$${Number(props.sede.tarifas[0].valor).toLocaleString('es-CO')}/h`
  : '—')
const puntuacion  = computed(() => Number(props.sede.puntuacion ?? 0))
const estrellas   = computed(() => Math.round(puntuacion.value))
const animDelay   = computed(() => `${props.index * 70}ms`)

// ── Reservar ──────────────────────────────
async function reservar() {
  if (!auth.isAuthenticated) { emit('login-required'); return }
  if (!disponible.value) { toast.warning('Este parqueadero no está disponible en este momento'); return }

  const result = await promptReserva(props.sede)
  if (!result) return  // usuario canceló

  try {
    const now = new Date()
    const [h, m, s] = result.tiempo.split(':').map(Number)
    const end = new Date(now.getTime() + (h * 3600 + m * 60 + s) * 1000)

    await reservasApi.crear(props.sede.uuid, {
      negocio:      props.sede.negocio.nit,
      piso:         '1',
      numero:       1,
      tipo_vehiculo: 3,
      tiempo:       result.tiempo,
      placa:        result.placa,
      hf_inicio:    now.toISOString(),
      hf_final:     end.toISOString(),
    })

    toast.success(`¡Reserva en ${props.sede.nombre} confirmada!`)
  } catch {
    toast.error('No se pudo crear la reserva. Intenta de nuevo.')
  }
}
</script>
