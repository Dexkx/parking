<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, CalendarCheck, XCircle, Receipt, Loader2 } from 'lucide-vue-next'
import { format, isPast } from 'date-fns'
import { es } from 'date-fns/locale'
import { reservasApi, negociosApi } from '@/api/axios'
import { useSwal } from '@/composables/useSwal'
import { useToast } from 'vue-toastification'

const toast = useToast()
const { showTicket, confirmAction } = useSwal()

const negocios  = ref([])
const nitActivo = ref('')
const reservas  = ref([])
const loading   = ref(true)
const query     = ref('')
const estado    = ref('all') // 'all' | 'activa' | 'completada' | 'cancelada'

onMounted(async () => {
  const res = await negociosApi.list()
  negocios.value = res.data?.results ?? res.data ?? []
  if (negocios.value.length > 0) {
    nitActivo.value = negocios.value[0].nit
    await cargar()
  }
  loading.value = false
})

async function cargar() {
  if (!nitActivo.value) return
  loading.value = true
  try {
    const res = await reservasApi.list(nitActivo.value)
    reservas.value = res.data?.results ?? res.data ?? []
  } finally { loading.value = false }
}

const lista = computed(() => {
  let l = [...reservas.value]
  if (query.value) {
    const q = query.value.toLowerCase()
    l = l.filter(r => r.placa?.toLowerCase().includes(q) || r.usuario?.toLowerCase().includes(q))
  }
  if (estado.value === 'activa')     l = l.filter(r => !isPast(new Date(r.hf_final)) && r.status !== 'Cancelado')
  if (estado.value === 'completada') l = l.filter(r => isPast(new Date(r.hf_final)) && r.status !== 'Cancelado')
  if (estado.value === 'cancelada')  l = l.filter(r => r.status === 'Cancelado')
  return l
})

const fmt = (iso) => format(new Date(iso), 'dd MMM · HH:mm', { locale: es })

function badgeClass(r) {
  if (r.status === 'Cancelado') return 'badge-red'
  if (isPast(new Date(r.hf_final))) return 'badge-blue'
  return 'badge-green'
}
function badgeLabel(r) {
  if (r.status === 'Cancelado') return 'Cancelada'
  if (isPast(new Date(r.hf_final))) return 'Completada'
  return 'Activa'
}

async function cancelar(r) {
  const { isConfirmed } = await confirmAction('¿Cancelar reserva?', `Placa <b>${r.placa}</b> — esta acción es irreversible.`, 'Sí, cancelar')
  if (!isConfirmed) return
  try {
    await reservasApi.cancelar(nitActivo.value, r.uuid)
    toast.success('Reserva cancelada')
    await cargar()
  } catch { toast.error('No se pudo cancelar') }
}
</script>

<template>
  <div class="p-6 max-w-screen-xl mx-auto">
    <div class="mb-7">
      <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Reservas</h1>
      <p class="text-t-secondary text-sm mt-1">Historial completo de reservas por negocio.</p>
    </div>

    <!-- Filtros -->
    <div class="flex flex-wrap gap-3 mb-5">
      <select class="input-dark w-56" v-model="nitActivo" @change="cargar">
        <option v-for="n in negocios" :key="n.nit" :value="n.nit">{{ n.nombre }}</option>
      </select>

      <div class="flex items-center gap-2 flex-1 min-w-[200px] bg-input border border-border rounded-sm px-3 py-2">
        <Search :size="13" class="text-t-muted shrink-0" />
        <input v-model="query" class="flex-1 bg-transparent border-none outline-none text-sm text-t-primary placeholder:text-t-muted"
               placeholder="Buscar por placa o usuario..." />
      </div>

      <div class="flex gap-1.5">
        <button v-for="e in [
          { key:'all', label:'Todas' },
          { key:'activa', label:'Activas' },
          { key:'completada', label:'Completadas' },
          { key:'cancelada', label:'Canceladas' },
        ]" :key="e.key"
          :class="['filter-chip', estado === e.key
            ? 'border-accent text-accent bg-accent/10'
            : 'border-border text-t-secondary hover:border-border-hover hover:text-t-primary']"
          @click="estado = e.key">
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
      <div class="table-row grid-cols-[1fr_1.2fr_1.2fr_1fr_1fr_1fr_100px] bg-surface/50">
        <div class="table-head-cell">Placa</div>
        <div class="table-head-cell">Entrada</div>
        <div class="table-head-cell">Salida</div>
        <div class="table-head-cell">Piso/Puesto</div>
        <div class="table-head-cell">Total</div>
        <div class="table-head-cell">Estado</div>
        <div class="table-head-cell justify-end">Acciones</div>
      </div>

      <div v-for="r in lista" :key="r.uuid"
           class="table-row grid-cols-[1fr_1.2fr_1.2fr_1fr_1fr_1fr_100px]">
        <div class="table-cell font-head font-bold text-accent tracking-widest text-xs">{{ r.placa }}</div>
        <div class="table-cell text-xs text-t-secondary">{{ fmt(r.hf_inicio) }}</div>
        <div class="table-cell text-xs text-t-secondary">{{ fmt(r.hf_final) }}</div>
        <div class="table-cell text-xs text-t-secondary">{{ r.piso ?? '—' }} · #{{ r.numero ?? '—' }}</div>
        <div class="table-cell font-head font-bold text-sm">${{ Number(r.valor_pagado ?? 0).toLocaleString('es-CO') }}</div>
        <div class="table-cell"><span :class="badgeClass(r)">{{ badgeLabel(r) }}</span></div>
        <div class="table-cell justify-end gap-1">
          <button class="btn-icon w-7 h-7" title="Ver ticket"
                  @click="showTicket({ ...r, negocio: negocios.find(n => n.nit === nitActivo)?.nombre })">
            <Receipt :size="13" />
          </button>
          <button v-if="!isPast(new Date(r.hf_final)) && r.status !== 'Cancelado'"
                  class="btn-icon w-7 h-7 hover:text-danger hover:border-danger/30" title="Cancelar"
                  @click="cancelar(r)">
            <XCircle :size="13" />
          </button>
        </div>
      </div>
    </div>

    <!-- Resumen -->
    <div v-if="!loading && lista.length > 0" class="mt-4 flex justify-end">
      <div class="text-xs text-t-muted">
        Total recaudado (filtro actual):
        <span class="font-head font-bold text-accent ml-1">
          ${{ lista.reduce((a, r) => a + Number(r.valor_pagado ?? 0), 0).toLocaleString('es-CO') }} COP
        </span>
      </div>
    </div>
  </div>
</template>
