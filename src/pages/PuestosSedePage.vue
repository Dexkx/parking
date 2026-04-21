<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, Trash2, ArrowLeft, LandPlot, DollarSign, Layers, MapPin, Check, X } from 'lucide-vue-next'
import CrudModal from '@/components/CrudModal.vue'
import { puestosSedeApi, sedesApi, catalogosApi } from '@/api/axios'
import { useToast } from 'vue-toastification'

const route  = useRoute()
const router = useRouter()
const toast  = useToast()

// const nit     = route.params.nit
const sedeId  = route.params.sede

const sede         = ref(null)
const puestos      = ref([])
const tiposVeh     = ref([])
const loading      = ref(true)
const saving       = ref(false)
const modal        = ref({ open: false })
const pisoActivo   = ref(null)

const emptyForm = () => ({ sede: sedeId, piso: '', numero: '', tipo_vehiculo: '' })
const form = ref(emptyForm())

onMounted(async () => {
  const [sedeRes, puestosRes, tvRes] = await Promise.all([
    sedesApi.list(),
    puestosSedeApi.list(sedeId),
    catalogosApi.tiposVehiculo(),
  ])
  const sedes = sedeRes.data?.results ?? sedeRes.data ?? []
  sede.value    = sedes.find(s => s.uuid === sedeId) ?? null
  puestos.value = puestosRes.data?.results ?? puestosRes.data ?? []
  tiposVeh.value = tvRes.data?.results ?? tvRes.data ?? []
  // Activar primer piso
  if (pisos.value.length > 0) pisoActivo.value = pisos.value[0]
  loading.value = false
})

// Pisos únicos extraídos de los puestos
const pisos = computed(() => [...new Set(puestos.value.map(p => p.piso))].sort())

// Puestos del piso activo
const puestosDelPiso = computed(() =>
  pisoActivo.value ? puestos.value.filter(p => p.piso === pisoActivo.value) : []
)

function openCreate() {
  form.value = emptyForm()
  if (pisoActivo.value) form.value.piso = pisoActivo.value
  modal.value.open = true
}
function closeModal() { modal.value.open = false }

async function handleSubmit() {
  saving.value = true
  try {
    await puestosSedeApi.create(sedeId, form.value)
    toast.success('Puesto creado')
    closeModal()
    const res = await puestosSedeApi.list(sedeId)
    puestos.value = res.data?.results ?? res.data ?? []
    if (!pisoActivo.value) pisoActivo.value = pisos.value[0]
  } catch (err) {
    toast.error(err.response?.data ? Object.values(err.response.data).flat().join(' · ') : 'Error al guardar')
  } finally { saving.value = false }
}

async function editStatus(item) {
  const accion = item.status === 'Activo' ? 'Desactivar' : 'Activar'
  if (!confirm(`¿${accion} el puesto "${item.numero}" del piso "${item.piso}"?`)) return
  try {
    const res = await puestosSedeApi.editStatus(sede.value.uuid, item.piso, item.numero, item.tipo_vehiculo.id, item.status === 'Activo' ? 'Inactivo' : 'Activo')
    toast.success(`Puesto ${res.data?.status}`)
    const found = puestos.value.find(n => n.piso === item.piso && n.numero === item.numero && n.tipo_vehiculo.id === item.tipo_vehiculo.id)
    if (found) found.status = res.data?.status
  } catch { toast.error('No se pudo cambiar el estado') }
}

const irTarifas = () => router.push({ name: 'tarifas', params: { sede: sedeId } })
</script>

<template>
  <div class="p-6 max-w-screen-lg mx-auto">

    <!-- Back -->
    <button class="flex items-center gap-1.5 text-xs text-t-muted hover:text-t-primary mb-5" @click="router.back()">
      <ArrowLeft :size="13" /> Volver a sedes
    </button>

    <!-- Header -->
    <div class="flex justify-between items-start mb-7">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <MapPin :size="14" class="text-blue" />
          <span class="text-xs text-t-muted">{{ sede?.nombre ?? sedeId }}</span>
        </div>
        <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Pisos y Puestos</h1>
        <p class="text-t-secondary text-sm mt-1">
          Organiza tu parqueadero por pisos. Cada puesto tiene un número y tipo de vehículo.
        </p>
      </div>
      <div class="flex gap-2">
        <button class="btn-ghost text-sm" @click="irTarifas">
          <DollarSign :size="14" /> Tarifas
        </button>
        <button class="btn-primary" @click="openCreate">
          <Plus :size="15" /> Nuevo puesto
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex gap-4">
      <div class="skeleton w-32 h-64 shrink-0" />
      <div class="flex-1 skeleton h-64" />
    </div>

    <div v-else class="flex gap-4">

      <!-- Selector de pisos (columna izquierda) -->
      <div class="w-32 shrink-0 flex flex-col gap-1.5">
        <div class="text-[10px] text-t-muted uppercase tracking-wider font-semibold mb-1 px-1">Pisos</div>

        <button v-for="piso in pisos" :key="piso"
          :class="['flex items-center gap-2 px-3 py-2 rounded-sm text-sm font-medium transition-all text-left',
                   pisoActivo === piso ? 'bg-accent/10 text-accent border border-accent/30' : 'text-t-secondary hover:text-t-primary hover:bg-white/5 border border-transparent']"
          @click="pisoActivo = piso">
          <Layers :size="13" /> {{ piso }}
        </button>

        <div v-if="pisos.length === 0" class="text-xs text-t-muted px-1 mt-2">
          Sin pisos.<br>Crea el primer puesto.
        </div>
      </div>

      <!-- Contenido del piso -->
      <div class="flex-1 card-dark rounded-lg overflow-hidden">

        <div v-if="!pisoActivo && pisos.length === 0" class="py-16 text-center text-t-muted">
          <LandPlot :size="36" :stroke-width="1" class="mx-auto mb-3" />
          <p class="font-head font-bold text-t-primary mb-1">Sin puestos</p>
          <p class="text-sm">Crea el primer puesto indicando el piso y número.</p>
        </div>

        <template v-else>
          <!-- Header tabla -->
          <div class="flex items-center justify-between px-5 py-3.5 border-b border-border bg-surface/50">
            <div class="flex items-center gap-2">
              <Layers :size="14" class="text-accent" />
              <span class="font-head font-bold text-sm text-t-primary">Piso {{ pisoActivo }}</span>
              <span class="badge-blue">{{ puestosDelPiso.length }} puesto{{ puestosDelPiso.length === 1 ? '' : 's' }}</span>
            </div>
          </div>

          <!-- Grid de puestos como casillas visuales -->
          <div class="p-4 grid grid-cols-5 md:grid-cols-8 gap-2">
            <div v-for="p in puestosDelPiso" :key="`${p.piso}-${p.numero}`"
                 class="group relative bg-input border border-border rounded-sm p-2 text-center hover:border-border-hover transition-all"
                 :class="{ '!bg-red-500/10': p.status === 'Inactivo' }">
              <div class="font-head font-bold text-t-primary text-sm">#{{ p.numero }}</div>
              <div class="text-[10px] text-t-muted mt-0.5 truncate">{{ p.tipo_vehiculo?.name ?? '—' }}</div>
              <span :class="p.status === 'Activo' ? 'badge-green' : 'badge-red'" class="mt-1">
                {{ p.status === 'Activo' ? 'Libre' : 'Inact.' }}
              </span>
              <!-- Btn desactivar/activar  al hover -->
              <button class="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                      @click="editStatus(p)" :class="{ 'bg-danger': p.status === 'Activo', 'bg-accent': p.status === 'Inactivo' }"
                      :title="p.status === 'Activo' ? 'Desactivar' : 'Activar'">

                <X v-if="p.status === 'Activo'" :size="12" class="text-white" />
                <Check v-else :size="12" class="text-white" />
                <!-- <span class="text-white text-[10px] leading-none">{{ p.status === 'Activo' ? '×' : '✓' }}</span> -->
              </button>
            </div>

            <!-- Btn agregar en el piso activo -->
            <button @click="openCreate"
                    class="border-2 border-dashed border-border rounded-sm p-2 text-center hover:border-accent/40 hover:text-accent transition-all text-t-muted flex flex-col items-center justify-center gap-1 min-h-[72px]">
              <Plus :size="16" />
              <span class="text-[10px]">Agregar</span>
            </button>
          </div>
        </template>
      </div>
    </div>

    <!-- Modal nuevo puesto -->
    <CrudModal :open="modal.open" title="Nuevo puesto" :loading="saving"
               submit-label="Crear puesto" @close="closeModal" @submit="handleSubmit">
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="label-dark">PISO</label>
          <input class="input-dark" v-model="form.piso" placeholder="Ej: 1, B1, Sótano" required />
        </div>
        <div>
          <label class="label-dark">N° DE PUESTO</label>
          <input class="input-dark" type="number" v-model="form.numero" min="1" placeholder="1" required />
        </div>
      </div>
      <div>
        <label class="label-dark">TIPO DE VEHÍCULO</label>
        <select class="input-dark" v-model="form.tipo_vehiculo" required>
          <option value="">Selecciona un tipo</option>
          <option v-for="tv in tiposVeh" :key="tv.id" :value="tv.id">{{ tv.name }}</option>
        </select>
      </div>
      <div class="bg-input/50 rounded-sm p-3 text-xs text-t-muted border border-border">
        💡 Puedes crear múltiples puestos con el mismo número pero diferente tipo de vehículo (ej: puesto 5 para carro y moto).
      </div>
    </CrudModal>

  </div>
</template>
