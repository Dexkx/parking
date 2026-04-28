<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import {
  LayoutDashboard, Building2, ParkingCircle,
  MapPin, Users, CalendarCheck, LogOut, ChevronRight
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const auth   = useAuthStore()
const route  = useRoute()
const router = useRouter()
const toast  = useToast()

const NAV = [
  { to: '/',            name: 'overview',      icon: LayoutDashboard, label: 'Overview',     section: null },
  { to: '/franquicias', name: 'franquicias',   icon: Building2,           label: 'Franquicias',  section: 'Estructura' },
  { to: '/negocios',    name: 'negocios',      icon: ParkingCircle,       label: 'Negocios',     section: null },
  { to: '/sedes',       name: 'sedes-general', icon: MapPin,   label: 'Sedes',        section: null },
  { to: '/clientes',    name: 'clientes',      icon: Users,           label: 'Clientes',     section: 'Operaciones' },
  { to: '/reservas',    name: 'reservas',      icon: CalendarCheck,   label: 'Reservas',     section: null },
]

// Activo: la ruta actual comienza con el path del ítem
// Caso especial para '/' exacto (overview)
const isActive = (item) => {
  if (item.to === '/') return route.path === '/'
  return route.path === item.to || route.path.startsWith(item.to + '/')
}

function handleLogout() {
  auth.logout()
  toast.info('Sesión cerrada')
  router.push('/login')
}

// Breadcrumb legible desde la ruta actual
const breadcrumb = computed(() => {
  const parts = route.path.split('/').filter(Boolean)
  return parts.map((p, i) => ({
    label: p.replace(/-/g, ' '),
    path:  '/' + parts.slice(0, i + 1).join('/'),
  }))
})
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-base">

    <!-- ─── Sidebar ─────────────────────────────────────────── -->
    <aside class="w-56 shrink-0 flex flex-col border-r border-border overflow-hidden"
           style="background:#0c0e14">

      <!-- Logo -->
      <div class="flex items-center gap-2.5 px-5 h-16 border-b border-border shrink-0">
        <div class="w-7 h-7 rounded-sm bg-accent flex items-center justify-center">
          <ParkingCircle :size="16" color="#000" :stroke-width="2.5" />
        </div>
        <div>
          <div class="font-head font-extrabold text-sm text-t-primary leading-tight">
            <span class="text-accent">P-</span>KAB
          </div>
          <div class="text-[10px] text-t-muted font-medium">Dashboard</div>
        </div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 overflow-y-auto py-4 px-3">
        <template v-for="item in NAV" :key="item.to">
          <!-- Separador de sección -->
          <div v-if="item.section"
               class="px-2 pt-4 pb-1.5 text-[10px] font-semibold text-t-muted uppercase tracking-widest">
            {{ item.section }}
          </div>

          <RouterLink :to="item.to"
            :class="['flex items-center gap-2.5 px-3 py-2 rounded-sm text-sm font-medium transition-all mb-0.5',
                     isActive(item)
                       ? 'bg-accent/10 text-accent'
                       : 'text-t-secondary hover:text-t-primary hover:bg-white/5']">
            <component :is="item.icon"
                       :size="15"
                       :stroke-width="isActive(item) ? 2.5 : 1.8" />
            {{ item.label }}
            <ChevronRight v-if="isActive(item) && item.to !== '/'"
                          :size="12" class="ml-auto" />
          </RouterLink>
        </template>
      </nav>

      <!-- Usuario -->
      <div class="px-3 py-3 border-t border-border shrink-0">
        <div class="flex items-center gap-2.5 px-2 py-2 rounded-sm">
          <div class="w-7 h-7 rounded-full bg-accent/10 border border-accent/30
                      flex items-center justify-center text-accent text-xs font-bold font-head shrink-0">
            {{ auth.userName.charAt(0).toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-xs font-semibold text-t-primary truncate">{{ auth.userName }}</div>
            <div class="text-[10px] text-t-muted">Administrador</div>
          </div>
          <button class="p-1.5 text-t-muted hover:text-danger transition-colors shrink-0"
                  @click="handleLogout" title="Cerrar sesión">
            <LogOut :size="13" />
          </button>
        </div>
      </div>
    </aside>

    <!-- ─── Main ─────────────────────────────────────────────── -->
    <div class="flex-1 flex flex-col overflow-hidden">

      <!-- Topbar -->
      <header class="h-16 shrink-0 flex items-center justify-between px-6 border-b border-border bg-surface">
        <!-- Breadcrumb -->
        <nav class="flex items-center gap-1.5 text-sm">
          <RouterLink to="/" class="text-t-muted hover:text-t-primary transition-colors">
            Dashboard
          </RouterLink>
          <template v-for="crumb in breadcrumb" :key="crumb.path">
            <ChevronRight :size="12" class="text-t-muted" />
            <RouterLink :to="crumb.path" class="text-t-primary font-medium capitalize">
              {{ crumb.label }}
            </RouterLink>
          </template>
        </nav>

        <!-- Acciones topbar -->
        <a href="/" target="_blank"
           class="flex items-center gap-1.5 text-xs text-t-muted hover:text-accent transition-colors
                  px-3 py-1.5 rounded-sm border border-border hover:border-accent/30">
          <MapPin :size="11" /> Ver sitio web
        </a>
      </header>

      <!-- Contenido de la página -->
      <main class="flex-1 overflow-y-auto">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>

    </div>
  </div>
</template>
