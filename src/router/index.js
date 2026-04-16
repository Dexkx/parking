/**
 * router/index.js
 * Rutas de la app con guardas de navegación.
 *
 * Rutas:
 *   /           → HomePage  (pública)
 *   /resultados → ResultadosPage (pública)
 *   /reservas   → MisReservasPage (requiere login)
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy-loading: cada página se carga solo cuando se necesita
const HomePage        = () => import('@/pages/HomePage.vue')
const ResultadosPage  = () => import('@/pages/ResultadosPage.vue')
const MisReservasPage = () => import('@/pages/MisReservasPage.vue')

const routes = [
  { path: '/',           name: 'home',     component: HomePage },
  { path: '/resultados', name: 'resultados', component: ResultadosPage },
  {
    path: '/reservas',
    name: 'reservas',
    component: MisReservasPage,
    meta: { requiresAuth: true },  // ← guarda activa
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// ── Guarda global: redirige a home si no hay sesión ──
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'home', query: { login: '1' } }
  }
})

export default router
