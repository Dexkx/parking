<script setup>
/**
 * ConfirmModal.vue
 * Modal de confirmación genérico — reemplaza useSwal confirmAction.
 *
 * Props:
 *   open        → Boolean
 *   title       → String
 *   message     → String (puede contener HTML básico)
 *   confirmText → String (default 'Confirmar')
 *   danger      → Boolean (si true, el botón confirmar es rojo)
 *
 * Emits:
 *   confirm
 *   cancel / close
 */
import { AlertTriangle, X } from 'lucide-vue-next'

defineProps({
  open:        { type: Boolean, required: true },
  title:       { type: String,  required: true },
  message:     { type: String,  default: '' },
  confirmText: { type: String,  default: 'Confirmar' },
  danger:      { type: Boolean, default: false },
})
defineEmits(['confirm', 'close'])
</script>

<template>
  <Transition name="modal">
    <div v-if="open"
         class="fixed inset-0 z-[9999] flex items-center justify-center p-4"
         style="background:rgba(0,0,0,0.75);backdrop-filter:blur(8px)"
         @click.self="$emit('close')">

      <div class="w-full max-w-sm bg-card border border-border rounded-xl overflow-hidden
                  shadow-[0_24px_80px_rgba(0,0,0,0.65)]">

        <div class="p-6 flex flex-col gap-4">
          <!-- Icono + título -->
          <div class="flex items-start gap-3">
            <div :class="['w-9 h-9 rounded-sm flex items-center justify-center shrink-0',
                          danger ? 'bg-danger/10 text-danger' : 'bg-warn/10 text-warn']">
              <AlertTriangle :size="18" />
            </div>
            <div>
              <h3 class="font-head font-bold text-base text-t-primary">{{ title }}</h3>
              <p v-if="message" class="text-sm text-t-secondary mt-1" v-html="message" />
            </div>
          </div>

          <!-- Botones -->
          <div class="flex gap-2 pt-1">
            <button class="btn-ghost flex-1 justify-center" @click="$emit('close')">
              Cancelar
            </button>
            <button :class="['flex-1 justify-center py-2 rounded-sm font-head font-bold text-sm transition-all flex items-center gap-2',
                             danger
                               ? 'bg-danger/10 border border-danger/30 text-danger hover:bg-danger/20'
                               : 'btn-primary']"
                    @click="$emit('confirm')">
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity .2s, transform .2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.96) translateY(10px); }
</style>
