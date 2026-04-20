<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, Trash2, ArrowLeft, DollarSign, Clock } from 'lucide-vue-next'
import CrudModal from '@/components/CrudModal.vue'
import { tarifasSedeApi, sedesApi, catalogosApi } from '@/api/axios'
import { useToast } from 'vue-toastification'
import { negociosApi } from '../api/axios'

const route  = useRoute()
const router = useRouter()
const toast  = useToast()

// const nit    = route.params.nit
const sedeId = route.params.sede

const sede      = ref(null)
const items     = ref([])
const tiposVeh  = ref([])
const loading   = ref(true)
const saving    = ref(false)
const modal     = ref({ open: false })

// Duración en horas y minutos → DurationField de Django espera HH:MM:SS
const durHoras = ref(1)
const durMins  = ref(0)

const emptyForm = () => ({ sede: sedeId, negocio: sede.value?.negocio.nit ?? '', tipo_vehiculo: '', piso: '', numero: null, valor: '' })
const form = ref(emptyForm())

onMounted(async () => {
  const [sedeRes, tarifasRes, tvRes] = await Promise.all([
    sedesApi.list(),
    tarifasSedeApi.list(sedeId),
    catalogosApi.tiposVehiculo(),
  ])
  const sedes = sedeRes.data?.results ?? sedeRes.data ?? []
  sede.value    = sedes.find(s => s.uuid === sedeId) ?? null
  console.log(sede.value)
  items.value   = tarifasRes.data?.results ?? tarifasRes.data ?? []
  tiposVeh.value = tvRes.data?.results ?? tvRes.data ?? []
  loading.value = false
})

function openCreate() {
  form.value = emptyForm()
  durHoras.value = 1; durMins.value = 0
  modal.value.open = true
}
function closeModal() { modal.value.open = false }

// Convertir horas + minutos → HH:MM:SS
function buildTiempo() {
  const h = String(durHoras.value).padStart(2, '0')
  const m = String(durMins.value).padStart(2, '0')
  return `${h}:${m}:00`
}

async function handleSubmit() {
  saving.value = true
  try {
    console.log(form.value)
    await tarifasSedeApi.create(sedeId, { ...form.value, tiempo: buildTiempo() })
    toast.success('Tarifa creada')
    closeModal()
    const res = await tarifasSedeApi.list(sedeId)
    items.value = res.data?.results ?? res.data ?? []
  } catch (err) {
    toast.error(err.response?.data ? Object.values(err.response.data).flat().join(' · ') : 'Error al guardar')
  } finally { saving.value = false }
}

async function handleDelete(item) {
  if (!confirm('¿Eliminar esta tarifa?')) return
  try {
    await tarifasSedeApi.remove(sedeId, `${item.tipo_vehiculo_id}-${item.tiempo}`)
    toast.success('Tarifa eliminada')
    items.value = items.value.filter(t => !(t.tipo_vehiculo_id === item.tipo_vehiculo_id && t.tiempo === item.tiempo))
  } catch { toast.error('No se pudo eliminar') }
}

// Formatear duración legible
function fmtTiempo(d) {
  if (!d) return '—'
  const parts = d.split(':')
  const h = parseInt(parts[0])
  const m = parseInt(parts[1])
  if (h && m) return `${h}h ${m}min`
  if (h) return `${h} hora${h > 1 ? 's' : ''}`
  return `${m} min`
}

const alcance = (t) => {
  if (t.numero) return `Puesto ${t.piso}·#${t.numero}`
  if (t.piso)   return `Piso ${t.piso}`
  return 'Toda la sede'
}
</script>

<template>
  <div class="p-6 max-w-screen-lg mx-auto">

    <!-- Back -->
    <button class="flex items-center gap-1.5 text-xs text-t-muted hover:text-t-primary mb-5" @click="router.back()">
      <ArrowLeft :size="13" /> Volver a puestos
    </button>

    <!-- Header -->
    <div class="flex justify-between items-start mb-7">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <DollarSign :size="14" class="text-accent" />
          <span class="text-xs text-t-muted">{{ sede?.nombre ?? sedeId }}</span>
        </div>
        <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Tarifas</h1>
        <p class="text-t-secondary text-sm mt-1">
          Define cuánto cobra la sede por fracción de tiempo. Puedes tener tarifas por toda la sede, por piso o por puesto específico.
        </p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus :size="15" /> Nueva tarifa
      </button>
    </div>

    <!-- Info alcance -->
    <div class="grid grid-cols-3 gap-3 mb-6">
      <div v-for="info in [
        { label: 'Tarifa general', desc: 'Aplica a toda la sede si no hay tarifa más específica', color: 'text-accent', bg: 'bg-accent/5 border-accent/15' },
        { label: 'Tarifa por piso', desc: 'Aplica al piso si no hay tarifa de puesto específico', color: 'text-blue', bg: 'bg-blue/5 border-blue/15' },
        { label: 'Tarifa por puesto', desc: 'Sobrescribe la tarifa de piso y sede. Máxima prioridad', color: 'text-purple', bg: 'bg-purple/5 border-purple/15' },
      ]" :key="info.label"
        :class="['rounded-lg p-3 border text-xs', info.bg]">
        <div :class="['font-semibold mb-0.5', info.color]">{{ info.label }}</div>
        <div class="text-t-muted">{{ info.desc }}</div>
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="flex flex-col gap-2">
      <div v-for="i in 4" :key="i" class="skeleton h-14" />
    </div>

    <!-- Vacío -->
    <div v-else-if="items.length === 0" class="card-dark rounded-lg py-14 text-center">
      <DollarSign :size="36" class="text-t-muted mx-auto mb-3" :stroke-width="1" />
      <p class="font-head font-bold text-t-primary mb-1">Sin tarifas</p>
      <p class="text-sm text-t-secondary">Crea al menos una tarifa general para esta sede.</p>
    </div>

    <!-- Tabla de tarifas -->
    <div v-else class="card-dark rounded-lg overflow-hidden">
      <!-- Header -->
      <div class="table-row grid-cols-[1.5fr_1fr_1fr_1.5fr_80px] bg-surface/50">
        <div class="table-head-cell">Tipo vehículo</div>
        <div class="table-head-cell">Duración</div>
        <div class="table-head-cell">Valor (COP)</div>
        <div class="table-head-cell">Alcance</div>
        <div class="table-head-cell justify-end">Acción</div>
      </div>

      <div v-for="t in items" :key="`${t.tipo_vehiculo_id}-${t.tiempo}`"
           class="table-row grid-cols-[1.5fr_1fr_1fr_1.5fr_80px]">
        <div class="table-cell gap-2">
          <div class="w-6 h-6 rounded bg-accent/10 flex items-center justify-center">
            <DollarSign :size="12" class="text-accent" />
          </div>
          <span class="font-medium">{{ t.tipo_vehiculo?.name ?? t.tipo_vehiculo }}</span>
        </div>
        <div class="table-cell">
          <div class="flex items-center gap-1 text-t-secondary">
            <Clock :size="12" /> {{ fmtTiempo(t.tiempo) }}
          </div>
        </div>
        <div class="table-cell font-head font-bold text-accent">
          ${{ Number(t.valor).toLocaleString('es-CO') }}
        </div>
        <div class="table-cell">
          <span :class="[
            !t.piso && !t.numero ? 'badge-green' :
            !t.numero ? 'badge-blue' : 'badge-purple'
          ]">{{ alcance(t) }}</span>
        </div>
        <div class="table-cell justify-end">
          <button class="btn-icon w-7 h-7 hover:text-danger hover:border-danger/30" @click="handleDelete(t)">
            <Trash2 :size="13" />
          </button>
        </div>
      </div>
    </div>

    <!-- Modal nueva tarifa -->
    <CrudModal :open="modal.open" title="Nueva tarifa" :loading="saving" size="lg"
               submit-label="Crear tarifa" @close="closeModal" @submit="handleSubmit">

      <div>
        <label class="label-dark">TIPO DE VEHÍCULO</label>
        <select class="input-dark" v-model="form.tipo_vehiculo" required>
          <option value="">Selecciona</option>
          <option v-for="tv in tiposVeh" :key="tv.id" :value="tv.id">{{ tv.name }}</option>
        </select>
      </div>

      <!-- Duración -->
      <div>
        <label class="label-dark">DURACIÓN (FRACCIÓN DE TIEMPO)</label>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-t-muted mb-1 block">Horas</label>
            <input class="input-dark" type="number" min="0" max="23" v-model="durHoras" />
          </div>
          <div>
            <label class="text-xs text-t-muted mb-1 block">Minutos</label>
            <input class="input-dark" type="number" min="0" max="59" step="5" v-model="durMins" />
          </div>
        </div>
        <div class="text-xs text-t-muted mt-1">
          Fracción configurada: <span class="text-accent font-semibold">{{ buildTiempo() }}</span>
        </div>
      </div>

      <!-- Valor -->
      <div>
        <label class="label-dark">VALOR EN COP</label>
        <div class="relative">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-t-muted text-sm">$</span>
          <input class="input-dark pl-7" type="number" min="0" v-model="form.valor" placeholder="5000" required />
        </div>
      </div>

      <!-- Alcance opcional -->
      <div class="border-t border-border pt-4">
        <div class="text-xs text-t-muted mb-3">
          <strong class="text-t-secondary">Alcance (opcional)</strong> — Deja vacío para que aplique a toda la sede.
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="label-dark">PISO (opcional)</label>
            <input class="input-dark" v-model="form.piso" placeholder="Ej: 1, B1" />
          </div>
          <div>
            <label class="label-dark">N° PUESTO (opcional)</label>
            <input class="input-dark" type="number" min="1" v-model="form.numero" placeholder="Ej: 5" />
          </div>
        </div>
      </div>
    </CrudModal>

  </div>
</template>
