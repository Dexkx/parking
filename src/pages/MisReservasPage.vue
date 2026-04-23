<script setup>
/**
 * MisReservasPage.vue
 * Usa TicketModal y ConfirmModal (Vue puro) en lugar de useSwal.
 */
import { ref, computed, onMounted } from 'vue'
import { CalendarClock, Receipt, XCircle, Clock } from 'lucide-vue-next'
import { formatDistanceToNow, isPast, format } from 'date-fns'
import { es } from 'date-fns/locale'
import { useAuthStore } from '@/stores/auth'
import { sedesApi, reservasApi } from '@/api/axios'
import { useToast } from 'vue-toastification'
import TicketModal   from '@/components/TicketModal.vue'
import ConfirmModal  from '@/components/ConfirmModal.vue'

const auth  = useAuthStore()
const toast = useToast()

// ── Estado ────────────────────────────────
const reservas = ref([])
const loading  = ref(true)
const tab      = ref('activas')

// Modales
const ticketModal  = ref({ open: false, reserva: null })
const confirmModal = ref({ open: false, reserva: null })

// ── Computed ──────────────────────────────
const activas   = computed(() => reservas.value.filter(r => !isPast(new Date(r.hf_final)) && r.status !== 'Cancelado'))
const historial = computed(() => reservas.value.filter(r => isPast(new Date(r.hf_final)) || r.status === 'Cancelado'))
const lista     = computed(() => tab.value === 'activas' ? activas.value : historial.value)

// ── Carga de reservas ──────────────────────
onMounted(async () => {
  try {
    // Obtener sedes desde el endpoint público y luego sus reservas
    const res  = await sedesApi.list()
    const seds = res.data?.results ?? res.data ?? []

    const promesas = seds.map(s =>
      reservasApi.mis(s.uuid)
        .then(r => (r.data?.results ?? r.data ?? []).map(rv => ({
          ...rv,
          negocio:    s.negocio?.nombre ?? s.nombre,
          negocio_id: s.uuid,
        })))
        .catch(() => [])
    )
    reservas.value = (await Promise.all(promesas)).flat()
  } finally {
    loading.value = false
  }
})

// ── Ver ticket ────────────────────────────
function abrirTicket(r) {
  ticketModal.value = { open: true, reserva: r }
}

// ── Cancelar reserva ──────────────────────
function pedirCancelacion(r) {
  confirmModal.value = { open: true, reserva: r }
}

async function confirmarCancelacion() {
  const r = confirmModal.value.reserva
  confirmModal.value.open = false
  if (!r) return
  try {
    await reservasApi.cancelar(r.negocio_id, r.uuid)
    reservas.value = reservas.value.map(rv =>
      rv.uuid === r.uuid ? { ...rv, status: 'Cancelado' } : rv
    )
    toast.success('Reserva cancelada correctamente')
  } catch {
    toast.error('No se pudo cancelar. Intenta de nuevo.')
  }
}

// ── Helpers de formato ────────────────────
const fmt     = (iso) => format(new Date(iso), 'dd MMM · HH:mm', { locale: es })
const reltime = (iso) => formatDistanceToNow(new Date(iso), { addSuffix: true, locale: es })

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
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-10">

    <!-- Encabezado -->
    <div class="mb-8">
      <h1 class="font-head font-extrabold text-3xl tracking-tight text-t-primary mb-1">
        Mis Reservas
      </h1>
      <p class="text-t-secondary text-sm">
        Hola, <span class="text-accent font-semibold">{{ auth.userName }}</span>.
        Aquí puedes ver y gestionar tus reservas.
      </p>
    </div>

    <!-- Tabs -->
    <div class="inline-flex gap-1 p-1 bg-card border border-border rounded-md mb-6">
      <button v-for="t in [
        { key:'activas',   label:`Activas (${activas.length})` },
        { key:'historial', label:`Historial (${historial.length})` },
      ]" :key="t.key"
        :class="['px-5 py-2 rounded text-xs font-semibold transition-all',
                 tab === t.key ? 'bg-surface text-accent shadow' : 'text-t-muted hover:text-t-secondary']"
        @click="tab = t.key">
        {{ t.label }}
      </button>
    </div>

    <!-- Skeleton -->
    <template v-if="loading">
      <div v-for="i in 3" :key="i" class="skeleton h-32 mb-3" />
    </template>

    <!-- Vacío -->
    <div v-else-if="lista.length === 0"
         class="flex flex-col items-center justify-center py-16 gap-3 text-t-muted">
      <CalendarClock :size="48" :stroke-width="1" />
      <p class="font-head font-bold text-lg text-t-primary">
        {{ tab === 'activas' ? 'No tienes reservas activas' : 'Sin historial' }}
      </p>
      <p class="text-sm text-center">
        {{ tab === 'activas'
          ? 'Busca un parqueadero y reserva tu espacio.'
          : 'Tus reservas completadas aparecerán aquí.' }}
      </p>
    </div>

    <!-- Lista de reservas -->
    <TransitionGroup v-else name="list" tag="div" class="flex flex-col gap-3">
      <article v-for="r in lista" :key="r.uuid"
               class="card-dark rounded-lg overflow-hidden">

        <!-- Cabecera -->
        <div class="flex justify-between items-start px-5 py-4 border-b border-border">
          <div>
            <p class="font-head font-bold text-base text-t-primary">
              {{ r.negocio ?? 'Parqueadero' }}
            </p>
            <p class="flex items-center gap-1 text-xs text-t-muted mt-0.5">
              <Clock :size="10" />
              {{ isPast(new Date(r.hf_final)) ? 'Terminó' : 'Termina' }}
              {{ reltime(r.hf_final) }}
            </p>
          </div>
          <span :class="badgeClass(r)">{{ badgeLabel(r) }}</span>
        </div>

        <!-- Stats grid -->
        <div class="grid grid-cols-4 gap-px bg-border">
          <div v-for="item in [
            { label: 'PLACA',       val: r.placa,                                accent: true },
            { label: 'PISO/PUESTO', val: `${r.piso ?? '—'} · #${r.numero ?? '—'}` },
            { label: 'ENTRADA',     val: fmt(r.hf_inicio) },
            { label: 'TOTAL',       val: `$${Number(r.valor_pagado ?? 0).toLocaleString('es-CO')}` },
          ]" :key="item.label" class="bg-card px-4 py-3">
            <div class="text-[10px] text-t-muted font-medium tracking-wider uppercase mb-1">
              {{ item.label }}
            </div>
            <div :class="['text-sm font-semibold',
                          item.accent ? 'text-accent font-head font-bold text-base' : 'text-t-primary']">
              {{ item.val }}
            </div>
          </div>
        </div>

        <!-- Acciones -->
        <div class="flex justify-end items-center gap-2 px-5 py-3 bg-input/50">
          <button class="btn-ghost text-xs px-3 py-1.5" @click="abrirTicket(r)">
            <Receipt :size="12" /> Ver ticket
          </button>
          <button v-if="!isPast(new Date(r.hf_final)) && r.status !== 'Cancelado'"
                  class="btn-danger text-xs px-3 py-1.5"
                  @click="pedirCancelacion(r)">
            <XCircle :size="12" /> Cancelar
          </button>
        </div>
      </article>
    </TransitionGroup>

  </div>

  <!-- Modales globales (Teleport para evitar z-index) -->
  <Teleport to="body">
    <TicketModal
      :open="ticketModal.open"
      :reserva="ticketModal.reserva"
      @close="ticketModal.open = false"
    />

    <ConfirmModal
      :open="confirmModal.open"
      title="¿Cancelar reserva?"
      :message="`Se cancelará tu espacio en <b>${confirmModal.reserva?.negocio ?? 'el parqueadero'}</b>. Esta acción es irreversible.`"
      confirm-text="Sí, cancelar"
      :danger="true"
      @close="confirmModal.open = false"
      @confirm="confirmarCancelacion"
    />
  </Teleport>
</template>

<style scoped>
.list-enter-active, .list-leave-active { transition: all .3s ease; }
.list-enter-from { opacity: 0; transform: translateY(10px); }
.list-leave-to   { opacity: 0; transform: translateX(-16px); }
</style>
