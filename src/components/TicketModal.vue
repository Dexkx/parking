<script setup>
/**
 * TicketModal.vue
 * Modal que muestra el ticket de una reserva — reemplaza useSwal showTicket.
 *
 * Props:
 *   open    → Boolean
 *   reserva → Objeto con datos de la reserva
 *
 * Emits:
 *   close
 */
import { X, MapPin, Car, Clock, Receipt, Star } from 'lucide-vue-next'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

const props = defineProps({
  open:    { type: Boolean,  required: true },
  reserva: { type: Object,   default: null },
})
defineEmits(['close'])

function fmt(iso) {
  if (!iso) return '—'
  try {
    return format(new Date(iso), "dd 'de' MMM yyyy · HH:mm", { locale: es })
  } catch { return iso }
}
</script>

<template>
  <Transition name="modal">
    <div v-if="open && reserva"
         class="fixed inset-0 z-[9999] flex items-center justify-center p-4"
         style="background:rgba(0,0,0,0.75);backdrop-filter:blur(10px)"
         @click.self="$emit('close')">

      <div class="w-full max-w-sm bg-card border border-border rounded-xl overflow-hidden
                  shadow-[0_24px_80px_rgba(0,0,0,0.65)]">

        <!-- Header -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-border">
          <div class="flex items-center gap-2">
            <Receipt :size="15" class="text-accent" />
            <span class="font-head font-bold text-base text-t-primary">Ticket de Reserva</span>
          </div>
          <button class="p-1.5 rounded-sm bg-input border border-border text-t-muted
                         hover:text-t-primary transition-colors"
                  @click="$emit('close')">
            <X :size="14" />
          </button>
        </div>

        <!-- Cuerpo del ticket -->
        <div class="p-5">
          <!-- Parqueadero + placa destacada -->
          <div class="rounded-lg p-4 mb-4"
               style="background:rgba(0,229,176,0.05);border:1px solid rgba(0,229,176,0.18)">
            <div class="text-[10px] text-t-muted uppercase tracking-wider mb-1">Parqueadero</div>
            <div class="font-head font-bold text-base text-t-primary mb-3">
              {{ reserva.sede.nombre ?? reserva.sede ?? '—' }}
            </div>
            <div class="text-[10px] text-t-muted uppercase tracking-wider mb-1">Placa</div>
            <div class="font-head font-extrabold text-3xl text-accent tracking-widest">
              {{ reserva.placa ?? '—' }}
            </div>
          </div>

          <!-- Grid de detalles -->
          <div class="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
            <div>
              <div class="text-[10px] text-t-muted uppercase tracking-wider mb-0.5">Piso / Puesto</div>
              <div class="text-t-primary font-medium">
                Piso {{ reserva.piso ?? '—' }} · #{{ reserva.numero ?? '—' }}
              </div>
            </div>
            <div>
              <div class="text-[10px] text-t-muted uppercase tracking-wider mb-0.5">Estado</div>
              <span :class="[
                'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold',
                reserva.status.value === 'Cancelado'
                  ? 'badge-red'
                  : reserva.status.value === 'Activo'
                  ? 'badge-green'
                  : 'badge-blue'
              ]">
                {{ reserva.status.value ?? 'Activa' }}
              </span>
            </div>
            <div>
              <div class="text-[10px] text-t-muted uppercase tracking-wider mb-0.5">Entrada</div>
              <div class="text-t-primary">{{ fmt(reserva.hf_inicio) }}</div>
            </div>
            <div>
              <div class="text-[10px] text-t-muted uppercase tracking-wider mb-0.5">Salida</div>
              <div class="text-t-primary">{{ fmt(reserva.hf_final) }}</div>
            </div>
          </div>

          <!-- Separador punteado estilo ticket -->
          <div class="relative my-4">
            <div class="border-t border-dashed border-border" />
            <div class="absolute -left-5 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-base" />
            <div class="absolute -right-5 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-base" />
          </div>

          <!-- Total pagado -->
          <div class="flex items-center justify-between">
            <div>
              <div class="text-[10px] text-t-muted uppercase tracking-wider mb-0.5">Total pagado</div>
              <div class="font-head font-extrabold text-2xl text-accent">
                ${{ Number(reserva.valor_pagado ?? 0).toLocaleString('es-CO') }}
                <span class="text-xs font-body font-normal text-t-muted ml-1">COP</span>
              </div>
            </div>
            <div class="w-12 h-12 rounded-xl bg-accent/10 border border-accent/20
                        flex items-center justify-center">
              <Receipt :size="22" class="text-accent" />
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-5 py-3 border-t border-border bg-surface/50">
          <button class="w-full btn-ghost justify-center text-sm" @click="$emit('close')">
            Cerrar
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity .2s, transform .2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.96) translateY(12px); }
</style>
