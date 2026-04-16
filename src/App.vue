<script setup>
/**
 * App.vue — Componente raíz
 *
 * Responsabilidades:
 *  - Montar el layout principal (Navbar + RouterView)
 *  - Controlar el LoginModal (open/close)
 *  - Cargar la sesión persistida en localStorage al iniciar
 *  - Detectar ?login=1 en la URL para abrir el modal automáticamente
 */
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppNavbar from '@/components/AppNavbar.vue'
import LoginModal from '@/components/LoginModal.vue'

const auth  = useAuthStore()
const route = useRoute()

const loginOpen = ref(false)

// ── Restaurar sesión al arrancar ─────────
onMounted(() => auth.loadSession())

// ── Abrir login si la URL tiene ?login=1 ─
watch(() => route.query.login, (val) => {
  if (val === '1') loginOpen.value = true
}, { immediate: true })
</script>

<template>
  <AppNavbar @open-login="loginOpen = true" />

  <!-- Modal de login global -->
  <LoginModal :open="loginOpen" @close="loginOpen = false" />

  <!-- Transición entre páginas -->
  <RouterView v-slot="{ Component, route }">
    <Transition name="route">
      <component
        :is="Component"
        :key="route.fullPath"
        @login-required="loginOpen = true"
      />
    </Transition>
  </RouterView>
</template>
