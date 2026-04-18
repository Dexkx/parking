<template>
  <nav class="sticky top-0 z-50 border-b border-border"
       style="background: rgba(8,10,15,0.85); backdrop-filter: blur(20px)">

    <div class="max-w-screen-xl mx-auto flex items-center justify-between h-16 px-6">

      <!-- Logo -->
      <RouterLink to="/" class="flex items-center gap-2 font-head font-extrabold text-xl tracking-tight">
        <MapPin :size="18" class="text-accent" :stroke-width="2.5" />
        <span><span class="text-accent">Park</span>App</span>
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

        <!-- Usuario logueado: chip con dropdown -->
        <template v-if="auth.isAuthenticated">
          <div class="relative" ref="dropdownRef">
            <!-- Chip clickeable -->
            <button
              class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-card border border-border text-sm text-t-secondary hover:border-border-hover transition-all"
              @click="dropdownOpen = !dropdownOpen">
              <div class="w-6 h-6 rounded-full bg-accent/10 border border-accent/40 flex items-center justify-center text-accent">
                <User :size="12" />
              </div>
              <span class="max-w-[120px] truncate">{{ auth.userName }}</span>
              <ChevronDown :size="12" :class="['transition-transform duration-200', dropdownOpen ? 'rotate-180' : '']" />
            </button>

            <!-- Dropdown -->
            <Transition name="dropdown">
              <div v-if="dropdownOpen"
                   class="absolute right-0 top-full mt-2 w-52 bg-card border border-border rounded-lg shadow-card overflow-hidden z-50">

                <!-- Info usuario -->
                <div class="px-4 py-3 border-b border-border">
                  <div class="text-xs font-semibold text-t-primary truncate">{{ auth.userName }}</div>
                  <div class="text-[11px] text-t-muted mt-0.5">{{ auth.user?.numero_id }}</div>
                </div>

                <!-- Opciones -->
                <div class="py-1.5">
                  <RouterLink to="/reservas"
                    class="flex items-center gap-2.5 px-4 py-2 text-sm text-t-secondary hover:text-t-primary hover:bg-white/5 transition-colors"
                    @click="dropdownOpen = false">
                    <BookOpen :size="14" /> Mis Reservas
                  </RouterLink>

                  <!-- Dashboard → subdominio externo -->
                  <a href="https://dashboard.p-kab.com" target="_blank"
                     class="flex items-center gap-2.5 px-4 py-2 text-sm text-t-secondary hover:text-accent hover:bg-accent/5 transition-colors"
                     @click="dropdownOpen = false">
                    <LayoutDashboard :size="14" />
                    <span>Dashboard</span>
                    <ExternalLink :size="10" class="ml-auto text-t-muted" />
                  </a>
                </div>

                <!-- Logout -->
                <div class="border-t border-border py-1.5">
                  <button
                    class="flex items-center gap-2.5 w-full px-4 py-2 text-sm text-danger hover:bg-danger/5 transition-colors"
                    @click="handleLogout">
                    <LogOut :size="14" /> Cerrar sesión
                  </button>
                </div>
              </div>
            </Transition>
          </div>
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
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { onClickOutside } from '@vueuse/core'
import {
  MapPin, BookOpen, LogOut, LogIn, User,
  ChevronDown, LayoutDashboard, ExternalLink
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const emit = defineEmits(['open-login'])

const auth         = useAuthStore()
const route        = useRoute()
const toast        = useToast()
const dropdownOpen = ref(false)
const dropdownRef  = ref(null)

// Cerrar dropdown al hacer clic fuera
onClickOutside(dropdownRef, () => { dropdownOpen.value = false })

function handleLogout() {
  auth.logout()
  dropdownOpen.value = false
  toast.info('Sesión cerrada')
}

const isActive = (path) => route.path === path
</script>

<style scoped>
.dropdown-enter-active, .dropdown-leave-active { transition: opacity .15s, transform .15s; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-6px) scale(0.97); }
</style>
