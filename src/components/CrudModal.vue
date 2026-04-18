<script setup>
/**
 * CrudModal.vue — Modal genérico para crear / editar registros.
 *
 * Props:
 *   open     → Boolean
 *   title    → String
 *   loading  → Boolean
 * Emits:
 *   close, submit
 * Slot:
 *   default → campos del formulario
 */
import { X, Loader2 } from 'lucide-vue-next'

defineProps({
  open:    { type: Boolean, required: true },
  title:   { type: String, required: true },
  loading: { type: Boolean, default: false },
  submitLabel: { type: String, default: 'Guardar' },
  size:    { type: String, default: 'md' }, // 'sm' | 'md' | 'lg'
})
defineEmits(['close', 'submit'])

const widths = { sm: 'max-w-sm', md: 'max-w-md', lg: 'max-w-xl' }
</script>

<template>
  <Transition name="modal">
    <div v-if="open"
         class="fixed inset-0 z-[200] flex items-center justify-center p-4"
         style="background:rgba(0,0,0,0.7);backdrop-filter:blur(6px)"
         @click.self="$emit('close')">

      <div :class="['w-full bg-card border border-border rounded-xl overflow-hidden shadow-[0_24px_80px_rgba(0,0,0,0.6)]', widths[size]]">

        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-border">
          <h3 class="font-head font-bold text-base text-t-primary">{{ title }}</h3>
          <button class="btn-icon w-7 h-7" @click="$emit('close')"><X :size="14" /></button>
        </div>

        <!-- Body -->
        <form @submit.prevent="$emit('submit')" class="p-6 flex flex-col gap-4">
          <slot />

          <!-- Footer -->
          <div class="flex justify-end gap-2 pt-2 border-t border-border mt-2">
            <button type="button" class="btn-ghost text-sm" @click="$emit('close')">Cancelar</button>
            <button type="submit" class="btn-primary text-sm" :disabled="loading">
              <Loader2 v-if="loading" :size="14" class="animate-spin" />
              <span v-else>{{ submitLabel }}</span>
            </button>
          </div>
        </form>

      </div>
    </div>
  </Transition>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity .2s, transform .2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.96) translateY(10px); }
</style>
