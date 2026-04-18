<script setup>
import { ref, onMounted, computed } from 'vue'
import { Building2, ParkingCircle, MapPin, Users, CalendarCheck, TrendingUp } from 'lucide-vue-next'
import StatCard from '@/components/StatCard.vue'
import { negociosApi, franquiciasApi, clientesApi, reservasApi } from '@/api/axios'
import { format, isToday } from 'date-fns'
import { es } from 'date-fns/locale'

const loading = ref(true)
const negocios = ref([])
const franquicias = ref([])
const reservasHoy = ref([])

onMounted(async () => {
  try {
    const [negRes, franRes] = await Promise.all([
      negociosApi.list(),
      franquiciasApi.list(),
    ])
    negocios.value = negRes.data?.results ?? negRes.data ?? []
    franquicias.value = franRes.data?.results ?? franRes.data ?? []

    // Reservas de hoy de todos los negocios
    const promesas = negocios.value.map(n =>
      reservasApi.list(n.nit).then(r => r.data?.results ?? r.data ?? []).catch(() => [])
    )
    const todas = (await Promise.all(promesas)).flat()
    reservasHoy.value = todas.filter(r => isToday(new Date(r.hf_inicio)))
  } finally {
    loading.value = false
  }
})

const totalSedes = computed(() => negocios.value.reduce((a, n) => a + (n.sedes_count ?? 0), 0))
const ingresoHoy = computed(() => reservasHoy.value.reduce((a, r) => a + Number(r.valor_pagado ?? 0), 0))
const today = format(new Date(), "EEEE dd 'de' MMMM", { locale: es })
</script>

<template>
  <div class="p-6 max-w-screen-lg mx-auto">

    <!-- Header -->
    <div class="mb-7">
      <p class="text-xs text-t-muted capitalize mb-1">{{ today }}</p>
      <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Vista general</h1>
    </div>

    <!-- Stats grid -->
    <div v-if="loading" class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div v-for="i in 4" :key="i" class="skeleton h-24" />
    </div>

    <div v-else class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <StatCard label="Franquicias" :value="franquicias.length" :icon="Building2" color="purple" />
      <StatCard label="Negocios" :value="negocios.length" :icon="ParkingCircle" color="accent"
        sub="Parqueaderos registrados" />
      <StatCard label="Sedes" :value="totalSedes" :icon="MapPin" color="blue" sub="Ubicaciones físicas" />
      <StatCard label="Reservas hoy" :value="reservasHoy.length" :icon="CalendarCheck" color="warn"
        :sub="`$${ingresoHoy.toLocaleString('es-CO')} COP`" />
    </div>

    <!-- Tabla de negocios recientes -->
    <div class="card-dark rounded-lg overflow-hidden">
      <div class="flex items-center justify-between px-5 py-4 border-b border-border">
        <h2 class="font-head font-bold text-base text-t-primary">Negocios</h2>
        <router-link to="/negocios" class="text-xs text-accent hover:underline">Ver todos →</router-link>
      </div>

      <div v-if="loading">
        <div v-for="i in 5" :key="i" class="skeleton h-12 mx-4 my-2" />
      </div>

      <div v-else-if="negocios.length === 0" class="py-12 text-center text-t-muted text-sm">
        No hay negocios registrados aún.
      </div>

      <template v-else>
        <table class="w-full border-collapse">
          <thead>
            <tr class="bg-surface/50 border-b border-border">
              <th class="table-head-cell">Nombre</th>
              <th class="table-head-cell">NIT</th>
              <th class="table-head-cell">Sedes</th>
              <th class="table-head-cell">Puntuación</th>
              <th class="table-head-cell">Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="n in negocios.slice(0, 8)" :key="n.nit"
              class="border-b border-border last:border-0 hover:bg-surface/30 transition-all duration-300 group">
              <td
                class="table-cell font-head font-bold text-t-primary text-sm group-hover:text-accent transition-colors">
                {{ n.nombre }}
              </td>
              <td class="table-cell text-xs font-mono text-t-secondary bg-surface/5">
                {{ n.nit }}-{{ n.numero_verificacion }}
              </td>
              <td class="table-cell">
                <span class="badge-blue">{{ n.sedes_count ?? 0 }} sedes</span>
              </td>
              <td class="table-cell text-warn font-semibold bg-surface/5">
                {{ n.puntuacion ? Number(n.puntuacion).toFixed(1) : '—' }} ★
              </td>
              <td class="table-cell">
                <span :class="n.status === 'Activo' ? 'badge-green' : 'badge-red'">{{ n.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </template>
    </div>
  </div>
</template>
