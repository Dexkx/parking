<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, CalendarCheck, X, Receipt, Plus, Check } from 'lucide-vue-next'
import { format, isPast } from 'date-fns'
import { es } from 'date-fns/locale'
import { useSwal } from '@/composables/useSwal'
import { useToast } from 'vue-toastification'
import CrudModal from '@/components/CrudModal.vue'
import { sedesApi, catalogosApi, reservasApi } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const toast = useToast()
const { showTicket, confirmAction } = useSwal()

const reservas = ref([])
const sedes = ref([])
const tiposVeh = ref([])
const loading = ref(true)
const query = ref('')
const estado = ref('all') // 'all' | 'activa' | 'completada' | 'cancelada'
const modal = ref({ open: false, mode: 'create', item: null })
const saving = ref(false)

const today = () => new Date().toISOString().split('T')[0]
const nowTime = () => {
  const d = new Date()
  return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

const emptyForm = () => ({
  sede: '',
  tipo_vehiculo: '',
  placa: '',
  fecha_inicio: today(),
  hora_inicio: nowTime(),
  usuario: ''
})
const form = ref(emptyForm())

onMounted(async () => {
  await Promise.all([
    cargar(),
    cargarCatalogos()
  ])
})

async function cargarCatalogos() {
  try {
    const [sRes, tvRes] = await Promise.all([
      sedesApi.list(),
      catalogosApi.tiposVehiculo()
    ])
    sedes.value = sRes.data?.results ?? sRes.data ?? []
    tiposVeh.value = tvRes.data?.results ?? tvRes.data ?? []
  } catch { toast.error('Error al cargar catálogos') }
}

async function cargar() {
  loading.value = true
  try {
    const res = await reservasApi.list()
    reservas.value = res.data
  } finally { loading.value = false }
}

const lista = computed(() => {
  let l = [...reservas.value]
  if (query.value) {
    const q = query.value.toLowerCase()
    l = l.filter(r => r.placa?.toLowerCase().includes(q) || r.usuario?.toLowerCase().includes(q))
  }

  switch (estado.value) {
    case 'activa':
      l = l.filter(r => !isPast(new Date(r.hf_final)) && r.status.value !== 'Cancelado')
      break
    case 'completada':
      l = l.filter(r => isPast(new Date(r.hf_final)) && r.status.value !== 'Cancelado')
      break
    case 'cancelada':
      l = l.filter(r => r.status.value === 'Cancelado')
      break
  }
  return l
})

const fmt = (iso) => format(new Date(iso), 'dd MMM · HH:mm', { locale: es })

function badgeClass(r) {
  switch (r.status.value) {
    case 'Cancelado': return 'badge-red'
    case 'Libre': return 'badge-blue'
    case 'Activo': return 'badge-green'
    default: return 'badge-gray'
  }
}

async function cancelar(r) {
  const { isConfirmed } = await confirmAction('¿Cancelar reserva?', `Placa <b>${r.placa}</b> — esta acción es irreversible.`, 'Sí, cancelar')
  if (!isConfirmed) return
  try {
    const rs = await reservasApi.cancelar(r.uuid)

    const rFind = reservas.value.find(rf => rf.uuid === r.uuid)
    rFind.status = rs.data.status

    toast.success('Reserva cancelada')
  } catch { toast.error('No se pudo cancelar') }
}

async function finalizar(r) {
  const { isConfirmed } = await confirmAction('¿Finalizar reserva?', `Placa <b>${r.placa}</b>`, 'Sí, finalizar')
  if (!isConfirmed) return

  try {
    const rs = await reservasApi.finalizar(r.uuid)

    const rFind = reservas.value.find(rf => rf.uuid === r.uuid)
    rFind.status = rs.data.status

    toast.success('Reserva finalizada/completada')
  } catch { toast.error('No se pudo finalizar') }
}

async function handleSubmit() {
  saving.value = true
  try {
    const inicio = new Date(`${form.value.fecha_inicio}T${form.value.hora_inicio}`)

    const data = {
      ...form.value,
      hf_inicio: inicio.toISOString(),
      negocio: sedes.value.find(s => s.uuid === form.value.sede)?.negocio?.nit,
      placa: form.value.placa.toUpperCase().replace(/\s/g, '').trim(),
    }

    if (!data.negocio) {
      toast.error('Error: No se pudo determinar el negocio de la sede')
      return
    }

    await reservasApi.create(data)
    toast.success('Reserva creada exitosamente')
    modal.value.open = false
    form.value = emptyForm()
    await cargar()
  } catch (err) {
    const d = err.response?.data
    toast.error(d ? Object.values(d).flat().join(' · ') : 'Error al guardar reserva')
  } finally { saving.value = false }
}
</script>

<template>
  <div>
    <div class="p-6 max-w-screen-xl mx-auto">
      <div class="flex justify-between items-center">
        <div>
          <div class="mb-7">
            <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Reservas</h1>
            <p class="text-t-secondary text-sm mt-1">Historial completo de reservas por negocio.</p>
          </div>
        </div>
        <div>
          <button class="btn-primary" @click="modal.open = true">
            <Plus :size="15" /> Nueva reserva
          </button>
        </div>
      </div>



      <!-- Filtros -->
      <div class="flex flex-wrap gap-3 mb-5">
        <!-- <select class="input-dark w-56" v-model="nitActivo" @change="cargar">
        <option v-for="n in negocios" :key="n.nit" :value="n.nit">{{ n.nombre }}</option>
      </select> -->

        <div class="flex items-center gap-2 flex-1 min-w-[200px] bg-input border border-border rounded-sm px-3 py-2">
          <Search :size="13" class="text-t-muted shrink-0" />
          <input v-model="query"
            class="flex-1 bg-transparent border-none outline-none text-sm text-t-primary placeholder:text-t-muted"
            placeholder="Buscar por placa o usuario..." />
        </div>

        <div class="flex gap-1.5">
          <button v-for="e in [
            { key: 'all', label: 'Todas' },
            { key: 'activa', label: 'Activas' },
            { key: 'completada', label: 'Completadas' },
            { key: 'cancelada', label: 'Canceladas' },
          ]" :key="e.key" :class="['filter-chip', estado === e.key
            ? 'border-accent text-accent bg-accent/10'
            : 'border-border text-t-secondary hover:border-border-hover hover:text-t-primary']" @click="estado = e.key">
            {{ e.label }}
          </button>
        </div>
      </div>

      <!-- Skeleton -->
      <div v-if="loading" class="flex flex-col gap-2">
        <div v-for="i in 6" :key="i" class="skeleton h-14" />
      </div>

      <!-- Vacío -->
      <div v-else-if="lista.length === 0" class="card-dark rounded-lg py-14 text-center">
        <CalendarCheck :size="36" class="text-t-muted mx-auto mb-3" :stroke-width="1" />
        <p class="font-head font-bold text-t-primary mb-1">Sin reservas</p>
        <p class="text-sm text-t-secondary">No hay reservas que coincidan con los filtros.</p>
      </div>

      <!-- Tabla -->
      <div v-else class="card-dark rounded-lg overflow-hidden">
        <table class="w-full border-collapse">
          <thead>
            <tr class="bg-surface/50 border-b border-border">
              <th class="table-head-cell">Placa</th>
              <th class="table-head-cell">Vehiculo</th>
              <th class="table-head-cell">Entrada</th>
              <th class="table-head-cell">Salida</th>
              <th class="table-head-cell">Piso/Puesto</th>
              <th class="table-head-cell">Total</th>
              <th class="table-head-cell">Estado</th>
              <th class="table-head-cell">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in lista" :key="r.uuid"
              class="border-b border-border last:border-0 hover:bg-surface/30 transition-all duration-300 group">
              <td
                class="table-cell font-head font-bold text-t-primary text-sm group-hover:text-accent transition-colors">
                {{ r.placa }}
              </td>
              <td
                class="table-cell font-head font-bold text-t-primary text-sm group-hover:text-accent transition-colors">
                {{ r.tipo_vehiculo.name }}
              </td>
              <td class="table-cell text-xs font-mono text-t-secondary bg-surface/5">
                {{ fmt(r.hf_inicio) }}
              </td>
              <td class="table-cell">
                <span class="badge-blue">{{ fmt(r.hf_final) }}</span>
              </td>
              <td class="table-cell text-warn font-semibold bg-surface/5">
                {{ r.piso }} · #{{ r.numero }}
              </td>
              <td class="table-cell">
                {{ Number(r.valor_pagado ?? 0).toLocaleString('es-CO') }}
              </td>
              <td class="table-cell">
                <span :class="badgeClass(r)">{{ r.status.value }}</span>
              </td>
              <td class="table-cell">
                <div class="w-full h-full flex flex-row gap-2 items-center justify-center">
                  <button class="btn-icon " title="Ver ticket" @click="showTicket(r)">
                    <Receipt :size="15" />
                  </button>
                  <button v-if="r.status.value == 'Activo'"
                    class="btn-icon hover:text-success hover:border-success/30" title="Finalizar" @click="finalizar(r)">
                    <Check :size="15" />
                  </button>
                  <button v-if="!isPast(new Date(r.hf_final)) && r.status.value !== 'Cancelado'"
                    class="btn-icon hover:text-danger hover:border-danger/30" title="Cancelar" @click="cancelar(r)">
                    <X :size="15" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Resumen -->
      <div v-if="!loading && lista.length > 0" class="mt-4 flex justify-end">
        <div class="text-xs text-t-muted">
          Total recaudado (filtro actual):
          <span class="font-head font-bold text-accent ml-1">
            ${{lista.reduce((a, r) => a + Number(r.valor_pagado ?? 0), 0).toLocaleString('es-CO')}} COP
          </span>
        </div>
      </div>
    </div>

    <CrudModal :open="modal.open" title="Nueva reserva (Manual)" :loading="saving"
      size="lg"
      @close="modal.open = false" @submit="handleSubmit">

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Sede -->
        <div class="col-span-1 md:col-span-2">
          <label class="label-dark">SEDE</label>
          <select class="input-dark" v-model="form.sede" required>
            <option value="">Selecciona una sede</option>
            <option v-for="s in sedes" :key="s.uuid" :value="s.uuid">
              {{ s.nombre }} ({{ s.negocio?.nombre }})
            </option>
          </select>
        </div>

        <!-- Tipo Vehículo -->
        <div>
          <label class="label-dark">TIPO DE VEHÍCULO</label>
          <select class="input-dark" v-model="form.tipo_vehiculo" required>
            <option value="">Selecciona tipo</option>
            <option v-for="tv in tiposVeh" :key="tv.id" :value="tv.id">{{ tv.name }}</option>
          </select>
        </div>

        <!-- Placa -->
        <div>
          <label class="label-dark">PLACA</label>
          <input class="input-dark uppercase font-mono" v-model="form.placa" placeholder="ABC 123" maxlength="7" required />
        </div>

        <!-- Fecha Inicio -->
        <div>
          <label class="label-dark">FECHA DE INICIO</label>
          <input class="input-dark" type="date" v-model="form.fecha_inicio" required />
        </div>

        <!-- Hora Inicio -->
        <div>
          <label class="label-dark">HORA DE INICIO</label>
          <input class="input-dark" type="time" v-model="form.hora_inicio" required />
        </div>

        <!-- Usuario (ID) -->
        <div class="col-span-1 md:col-span-2">
          <label class="label-dark">DOCUMENTO USUARIO (PARA REGISTRO)</label>
          <div class="flex gap-2">
            <input class="input-dark flex-1" v-model="form.usuario" placeholder="CC / NIT" required />
          </div>
        </div>
      </div>

      <div class="mt-4 p-3 bg-accent/5 border border-accent/20 rounded text-xs text-t-secondary">
        <p><strong>Nota:</strong> Esta reserva se creará sin tarifa asignada por defecto. El sistema calculará el cobro al finalizar la estancia basándose en el tiempo transcurrido.</p>
      </div>

    </CrudModal>
  </div>
</template>
