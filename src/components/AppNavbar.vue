<template>
  <!-- nav sticky con blur glassmorphism -->
  <nav class="sticky top-0 z-[9999] border-b border-border"
       style="background: rgba(8,10,15,0.85); backdrop-filter: blur(20px)">

    <div class="max-w-screen-xl mx-auto flex items-center justify-between h-16 px-6">

      <!-- Logo -->
      <RouterLink to="/" class="flex items-center gap-2 font-head font-extrabold text-xl tracking-tight">
        <MapPin :size="18" class="text-accent" :stroke-width="2.5" />
        <span><span class="text-accent">P-</span>KAB</span>
      </RouterLink>

      <!-- Links centrales -->
      <div class="flex items-center gap-1">
        <RouterLink to="/"
          :class="['flex items-center gap-1.5 px-3.5 py-1.5 rounded-sm text-sm font-medium transition-all',
                   isActive('/') ? 'bg-accent/10 text-accent' : 'text-t-secondary hover:text-t-primary']">
          <MapPin :size="14" /> Mapa
        </RouterLink>

        <RouterLink to="/resultados"
          :class="['flex items-center gap-1.5 px-3.5 py-1.5 rounded-sm text-sm font-medium transition-all',
                   isActive('/resultados') ? 'bg-accent/10 text-accent' : 'text-t-secondary hover:text-t-primary']">
          Parqueaderos
        </RouterLink>

        <RouterLink v-if="auth.isAuthenticated" to="/reservas"
          :class="['flex items-center gap-1.5 px-3.5 py-1.5 rounded-sm text-sm font-medium transition-all',
                   isActive('/reservas') ? 'bg-accent/10 text-accent' : 'text-t-secondary hover:text-t-primary']">
          <BookOpen :size="14" /> Mis Reservas
        </RouterLink>
      </div>

      <!-- Área de usuario -->
      <div class="flex items-center gap-2.5">

        <!-- Usuario logueado -->
        <template v-if="auth.isAuthenticated">
          <!-- Chip nombre -->
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-card border border-border text-sm text-t-secondary">
            <div class="w-6 h-6 rounded-full bg-accent/10 border border-accent/40 flex items-center justify-center text-accent">
              <User :size="12" />
            </div>
            <span class="max-w-[120px] truncate">{{ auth.userName }}</span>
          </div>
          <!-- Btn logout -->
          <button class="btn-ghost text-xs px-3 py-1.5" @click="handleLogout">
            <LogOut :size="13" /> Salir
          </button>
        </template>

        <!-- No logueado -->
        <template v-else>
          <button class="btn-primary text-sm px-4 py-2" @click="$emit('open-login')">
            <LogIn :size="14" /> Ingresar
          </button>
        </template>

      </div>
    </div>
  </nav>
</template>

<script setup>
/**
 * AppNavbar.vue
 * Barra de navegación fija con:
 *  - Logo con acento de color
 *  - Links de navegación con estado activo
 *  - Chip del usuario autenticado
 *  - Botón login / logout
 */
import { RouterLink, useRoute } from 'vue-router'
import { MapPin, BookOpen, LogOut, LogIn, User } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const emit = defineEmits(['open-login'])

const auth  = useAuthStore()
const route = useRoute()
const toast = useToast()

function handleLogout() {
  auth.logout()
  toast.info('Sesión cerrada')
}

const isActive = (path) => route.path === path
</script>
