<script setup>
/**
 * App.vue del dashboard
 *
 * Muestra el DashboardLayout (sidebar + topbar) para todas las rutas
 * excepto /login, que se renderiza limpia sin layout.
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DashboardLayout from '@/layouts/DashboardLayout.vue'

const route = useRoute()
const usaLayout = computed(() => route.name !== 'login')
</script>

<template>
  <!-- Rutas protegidas: con sidebar -->
  <DashboardLayout v-if="usaLayout" />

  <!-- Login: página limpia sin sidebar -->
  <RouterView v-else />
</template>
