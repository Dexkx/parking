<script setup>
/**
 * ReservaModal.vue
 * Modal de reserva en Vue puro — sin SweetAlert2.
 *
 * Props:
 *   open  → Boolean
 *   sede  → objeto de la sede a reservar
 *
 * Emits:
 *   close
 *   confirmada  → la reserva fue creada exitosamente
 *
 * Flujo:
 *  1. Al abrir, carga las tarifas disponibles de la sede
 *  2. El usuario selecciona tipo de vehículo → filtra tarifas compatibles
 *  3. Selecciona duración → muestra precio calculado automáticamente
 *  4. Ingresa placa → se puede verificar contra vehículos registrados
 *  5. Al confirmar → llama al backend y emite 'confirmada'
 */
import { ref, computed, watch, onMounted } from 'vue'
import { X, Car, Clock, DollarSign, MapPin, Loader2, ChevronDown, Check } from 'lucide-vue-next'
import { sedesApi, reservasApi, catalogosApi, vehiculosApi } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const props = defineProps({
  open: Boolean,
  sede: { type: Object, required: true },
})
const emit = defineEmits(['close', 'confirmada'])

const auth  = useAuthStore()
const toast = useToast()

// ── Estado ──────────────────────────────────────────
const loading       = ref(false)   // cargando tarifas iniciales
const saving        = ref(false)   // guardando reserva
const tarifas       = ref([])      // todas las tarifas de la sede
const tiposVehiculo = ref([])      // tipos de vehículo disponibles
const vehiculosUser = ref([])      // placas registradas del usuario

const emptyForm = {
  negocio:       props.sede.negocio.nit,
  sede:          props.sede.uuid,
  tipo_vehiculo: '',  // id del tipo de vehículo
  tarifa:        null, // objeto tarifa seleccionada
  placa:         '',   // placa manual o seleccionada
  fecha_inicio:  today(),  // fecha de inicio
  hora_inicio:   horaActual(), // hora de inicio
}
const form = ref(emptyForm)

// ── Computed ─────────────────────────────────────────
// Tipos de vehículo únicos disponibles en las tarifas
const tiposDisponibles = computed(() => {
  const vistos = new Set()
  return tarifas.value.filter(t => {
    const key = t.tipo_vehiculo.id
    if (vistos.has(key)) return false
    vistos.add(key)
    return true
  }).map(t => ({
    id:   t.tipo_vehiculo.id,
    name: t.tipo_vehiculo.name,
  }))
})

const nombreVehiculo = computed(() => {
  if (!form.value.tipo_vehiculo) return ''
  // Si es un objeto (vía seleccionarVehiculo) o un ID (vía select)
  const id = form.value.tipo_vehiculo
  const encontrado = tiposDisponibles.value.find(t => t.id === id)
  return encontrado ? encontrado.name : id
})

// Tarifas filtradas por el tipo de vehículo seleccionado
const tarifasFiltradas = computed(() => {
  if (!form.value.tipo_vehiculo) return []
  return tarifas.value.filter(t =>
    t.tipo_vehiculo.id === form.value.tipo_vehiculo
  ).sort((a, b) => duracionSeg(a.tiempo) - duracionSeg(b.tiempo))
})

// Precio total basado en tarifa seleccionada (No se muestra si no hay tarifa)
const precioTotal = computed(() => {
  if (!form.value.tarifa) return null
  return Number(form.value.tarifa.valor)
})

const canSubmit = computed(() =>
  form.value.tipo_vehiculo &&
  form.value.placa.trim().length >= 5 &&
  !saving.value
)

// ── Carga al abrir ────────────────────────────────────
watch(() => props.open, async (val) => {
  if (!val) return
  resetForm()
  await cargarDatos()
})

async function cargarDatos() {
  loading.value = true
  try {
    const [tarifasRes, tvRes] = await Promise.all([
      sedesApi.tarifas(props.sede.uuid),
      catalogosApi.tiposVehiculo(),
    ])
    tarifas.value       = tarifasRes.data?.results ?? tarifasRes.data ?? []
    tiposVehiculo.value = tvRes.data?.results      ?? tvRes.data      ?? []

    // Si el usuario está logueado, cargar sus vehículos
    if (auth.isAuthenticated && auth.user?.numero_id) {
      try {
        const vRes = await vehiculosApi.list(auth.user.numero_id)
        vehiculosUser.value = vRes.data?.results ?? vRes.data ?? []
      } catch { vehiculosUser.value = [] }
    }

    // Si solo hay un tipo de vehículo, pre-seleccionarlo
    if (tiposDisponibles.value.length === 1) {
      form.value.tipo_vehiculo = tiposDisponibles.value[0].id
    }
  } finally {
    loading.value = false
  }
}

// ── Reset ────────────────────────────────────────────
function resetForm() {
  form.value = emptyForm
}

// Cuando cambia el tipo de vehículo, limpiar tarifa seleccionada
watch(() => form.value.tipo_vehiculo, () => {
  form.value.tarifa = null
})

// Si el usuario selecciona un vehículo registrado, autocompletar placa
function seleccionarVehiculo(v) {
  form.value.placa         = v.placa
  form.value.tipo_vehiculo = v.tipo_vehiculo?.name ?? v.tipo_vehiculo
}

// ── Guardar ──────────────────────────────────────────
async function handleSubmit() {
  if (!canSubmit.value) return
  saving.value = true
  try {
    const inicio = new Date(`${form.value.fecha_inicio}T${form.value.hora_inicio}`)

    const data = {
      ...form.value,
      tarifa:       form.value.tarifa?.uuid ?? null,
      piso:         form.value.tarifa?.piso ?? null,
      numero:       form.value.tarifa?.numero ?? null,
      tiempo:       form.value.tarifa?.tiempo ?? null,
      placa:        form.value.placa.toUpperCase().replace(/\s/g, '').trim(),
      hf_inicio:    inicio.toISOString(),
      hf_final:     null, // Se calculará al salir
    }
    await reservasApi.crear(auth.user.numero_id, data)

    emit('confirmada', {
      sede:     props.sede.nombre,
      placa:    form.value.placa.toUpperCase(),
      precio:   precioTotal.value,
      inicio,
    })
    emit('close')
  } catch (err) {
    const data = err.response?.data
    const msg  = data ? Object.values(data).flat().join(' · ') : 'No se pudo crear la reserva'
    toast.error(msg)
  } finally { saving.value = false }
}

// ── Helpers ───────────────────────────────────────────
function duracionSeg(t) {
  if (!t) return 0
  const [h, m, s] = t.split(':').map(Number)
  return h * 3600 + m * 60 + (s ?? 0)
}

function fmtDuracion(t) {
  if (!t) return '—'

  // Regex para: "30 00:00:00", "1 day, 01:02:03", "15:30:00", "00:00:00.123"
  const match = t.trim().match(/^(?:(\d+)\s+(?:days?,\s*)?)?(\d+):(\d+):(\d+)(?:\.\d+)?$/)
  if (!match) return t

  const d = parseInt(match[1] || 0)
  const h = parseInt(match[2] || 0)
  const m = parseInt(match[3] || 0)
  const s = parseInt(match[4] || 0)
  const totalSeg = (d * 86400) + (h * 3600) + (m * 60) + s

  const meses = Math.floor(totalSeg / (86400 * 30))
  const dias  = Math.floor((totalSeg % (86400 * 30)) / 86400)
  const horas = Math.floor((totalSeg % 86400) / 3600)
  const mins  = Math.floor((totalSeg % 3600) / 60)

  const partes = []
  if (meses) partes.push(`${meses} mes${meses > 1 ? 'es' : ''}`)
  if (dias)  partes.push(`${dias} día${dias > 1 ? 's' : ''}`)
  if (horas) partes.push(`${horas} hora${horas > 1 ? 's' : ''}`)
  if (mins)  partes.push(`${mins} min`)

  return partes.length ? partes.join(' ') : '0 min'
}

function today() {
  return new Date().toISOString().split('T')[0]
}
function horaActual() {
  const d = new Date()
  return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

function alcanceTarifa(t) {
  if (t.numero) return `Puesto ${t.piso}·#${t.numero}`
  if (t.piso)   return `Piso ${t.piso}`
  return 'General'
}
</script>

<template>
  <Transition name="modal">
    <div v-if="open && sede"
         class="fixed inset-0 z-[1000] flex items-center justify-center p-4"
         style="background:rgba(0,0,0,0.75);backdrop-filter:blur(10px)"
         @click.self="$emit('close')">

      <div class="w-full max-w-lg bg-card border border-border rounded-xl overflow-hidden shadow-[0_24px_80px_rgba(0,0,0,0.65)] overflow-y-auto max-h-full">

        <!-- ── Header ── -->
        <div class="flex items-start justify-between px-6 py-5 border-b border-border">
          <div>
            <h2 class="font-head font-extrabold text-xl text-t-primary tracking-tight">
              Reservar espacio
            </h2>
            <div class="flex items-center gap-1.5 mt-1 text-sm text-t-secondary">
              <MapPin :size="12" class="text-accent shrink-0" />
              <span class="truncate">{{ sede.nombre }}</span>
              <span class="text-t-muted">·</span>
              <span class="text-xs text-t-muted truncate">{{ sede.direccion }}</span>
            </div>
          </div>
          <button class="p-1.5 rounded-sm bg-input border border-border text-t-muted
                         hover:text-t-primary transition-colors shrink-0"
                  @click="$emit('close')">
            <X :size="15" />
          </button>
        </div>

        <!-- ── Cargando ── -->
        <div v-if="loading" class="flex items-center justify-center py-16 gap-3 text-t-muted">
          <Loader2 :size="20" class="animate-spin" />
          <span class="text-sm">Cargando tarifas disponibles...</span>
        </div>

        <!-- ── Sin tarifas ── -->
        <div v-else-if="tarifas.length === 0"
             class="py-14 text-center text-t-muted px-6">
          <DollarSign :size="36" :stroke-width="1" class="mx-auto mb-3" />
          <p class="font-head font-bold text-t-primary mb-1">Sin tarifas configuradas</p>
          <p class="text-sm">Esta sede aún no tiene tarifas disponibles. Intenta más tarde.</p>
        </div>

        <!-- ── Formulario ── -->
        <form v-else @submit.prevent="handleSubmit" class="p-6 flex flex-col gap-5">

          <!-- Vehículos registrados del usuario (si los tiene) -->
          <div v-if="vehiculosUser.length > 0">
            <label class="text-xs font-medium text-t-muted tracking-wider uppercase block mb-2">
              TUS VEHÍCULOS
            </label>
            <div class="flex gap-2 flex-wrap">
              <button v-for="v in vehiculosUser" :key="v.placa"
                      type="button"
                      :class="['flex items-center gap-1.5 px-3 py-1.5 rounded-sm text-xs font-semibold border transition-all',
                               form.placa === v.placa
                                 ? 'bg-accent/10 border-accent text-accent'
                                 : 'bg-input border-border text-t-secondary hover:border-border-hover']"
                      @click="seleccionarVehiculo(v)">
                <Car :size="11" />
                {{ v.placa }}
                <Check v-if="form.placa === v.placa" :size="10" />
              </button>
            </div>
          </div>

          <!-- Placa -->
          <div>
            <label class="text-xs font-medium text-t-muted tracking-wider uppercase block mb-1.5">
              PLACA DEL VEHÍCULO
            </label>
            <input class="input-dark tracking-widest uppercase font-mono text-base text-t-primary"
                   v-model="form.placa"
                   maxlength="7"
                   placeholder="Ej: ABC 123"
                   required />
          </div>

          <!-- Tipo de vehículo -->
          <div>
            <label class="text-xs font-medium text-t-muted tracking-wider uppercase block mb-1.5">
              TIPO DE VEHÍCULO
            </label>
            <select class="input-dark" v-model="form.tipo_vehiculo" required>
              <option value="">Selecciona un tipo</option>
              <option v-for="tv in tiposDisponibles" :key="tv.id" :value="tv.id">{{ tv.name }}</option>
            </select>
          </div>

          <!-- Info de Tarifa (Opcional o informativa) -->
          <div v-if="form.tipo_vehiculo" class="bg-input/50 border border-border rounded-lg p-4">
            <div class="flex items-center gap-2 text-t-secondary mb-2">
              <Clock :size="14" class="text-accent" />
              <span class="text-xs font-bold uppercase tracking-wider">Tarifas disponibles</span>
            </div>
            <p class="text-xs text-t-muted mb-3">
              El cobro se realizará según el tiempo efectivo de uso.
            </p>
            <div class="flex flex-col gap-1.5">
              <div v-for="t in tarifasFiltradas" :key="`${t.tipo_vehiculo.id}-${t.tiempo}`"
                   class="flex justify-between items-center text-sm py-1 border-b border-border/50 last:border-0">
                <span class="text-t-secondary">{{ fmtDuracion(t.tiempo) }}</span>
                <span class="font-head font-bold text-t-primary">
                  ${{ Number(t.valor).toLocaleString('es-CO') }}
                </span>
              </div>
            </div>
          </div>

          <!-- Fecha y hora de inicio -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium text-t-muted tracking-wider uppercase block mb-1.5">
                FECHA DE INICIO
              </label>
              <input class="input-dark" type="date" v-model="form.fecha_inicio"
                     :min="today()" required />
            </div>
            <div>
              <label class="text-xs font-medium text-t-muted tracking-wider uppercase block mb-1.5">
                HORA DE INICIO
              </label>
              <input class="input-dark" type="time" v-model="form.hora_inicio" required />
            </div>
          </div>

          <!-- Resumen de la reserva -->
          <div v-if="form.placa"
               class="rounded-lg p-4 border"
               style="background:rgba(0,229,176,0.05);border-color:rgba(0,229,176,0.2)">
            <div class="text-xs font-semibold text-accent tracking-wider uppercase mb-3">
              RESUMEN DE TU RESERVA
            </div>
            <div class="grid grid-cols-2 gap-y-2.5 text-sm">
              <div class="text-t-muted">Sede</div>
              <div class="text-t-primary font-medium text-right">{{ sede.nombre }}</div>

              <div class="text-t-muted">Placa</div>
              <div class="text-accent font-head font-bold text-right tracking-widest">
                {{ form.placa.toUpperCase() }}
              </div>

              <div class="text-t-muted">Vehículo</div>
              <div class="text-t-primary text-right">{{ nombreVehiculo }}</div>

              <div class="text-t-muted">Entrada</div>
              <div class="text-t-primary text-right">
                {{ form.fecha_inicio }} {{ form.hora_inicio }}
              </div>

              <div class="text-t-muted">Salida</div>
              <div class="text-t-primary text-right font-semibold">Calculado al salir</div>

              <div class="col-span-2 border-t border-border/50 pt-2.5 mt-0.5 flex justify-between items-center">
                <span class="text-t-muted text-xs uppercase tracking-wider">Total a pagar</span>
                <span class="font-head font-extrabold text-xl text-accent">
                  Pendiente
                </span>
              </div>
            </div>
          </div>

          <!-- Acciones -->
          <div class="flex gap-2 pt-1">
            <button type="button" class="btn-ghost flex-1 justify-center" @click="$emit('close')">
              Cancelar
            </button>
            <button type="submit" class="btn-primary flex-1 justify-center py-3"
                    :disabled="!canSubmit">
              <Loader2 v-if="saving" :size="15" class="animate-spin" />
              <span v-else>Confirmar reserva →</span>
            </button>
          </div>

        </form>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity .2s, transform .2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.96) translateY(12px); }
</style>
