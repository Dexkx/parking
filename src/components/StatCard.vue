<script setup>
defineProps({
  label:  { type: String, required: true },
  value:  { type: [String, Number], required: true },
  sub:    { type: String, default: '' },
  color:  { type: String, default: 'accent' }, // 'accent' | 'blue' | 'purple' | 'warn'
  icon:   { type: [Object, Function], default: null },
})

const colors = {
  accent: { bg: 'bg-accent/10', text: 'text-accent', border: 'border-accent/20' },
  blue:   { bg: 'bg-blue/10',   text: 'text-blue',   border: 'border-blue/20' },
  purple: { bg: 'bg-purple/10', text: 'text-purple',  border: 'border-purple/20' },
  warn:   { bg: 'bg-warn/10',   text: 'text-warn',    border: 'border-warn/20' },
}
</script>

<template>
  <div class="card-dark rounded-lg p-5 flex items-start gap-4 animate-fade-up">
    <!-- Icono -->
    <div v-if="icon" :class="['w-10 h-10 rounded-sm flex items-center justify-center shrink-0', colors[color].bg, colors[color].text]">
      <component :is="icon" :size="18" />
    </div>
    <!-- Info -->
    <div class="flex-1 min-w-0">
      <div class="text-xs text-t-muted font-medium uppercase tracking-wider mb-1">{{ label }}</div>
      <div :class="['font-head font-extrabold text-2xl tracking-tight', colors[color].text]">{{ value }}</div>
      <div v-if="sub" class="text-xs text-t-muted mt-0.5">{{ sub }}</div>
    </div>
  </div>
</template>
