import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const LoginPage                    = () => import('@/pages/LoginPage.vue')
const OverviewPage                 = () => import('@/pages/OverviewPage.vue')
const FranquiciasPage              = () => import('@/pages/FranquiciasPage.vue')
const ColaboradoresFranquiciaPage  = () => import('@/pages/ColaboradoresFranquiciaPage.vue')
const NegociosPage                 = () => import('@/pages/NegociosPage.vue')
const ColaboradoresNegocioPage     = () => import('@/pages/ColaboradoresNegocioPage.vue')
const SedesGeneralPage             = () => import('@/pages/SedesGeneralPage.vue')   // ← menú sidebar
const ColaboradoresSedePage        = () => import('@/pages/ColaboradoresSedePage.vue')
const PuestosSedePage                  = () => import('@/pages/PuestosSedePage.vue')
const TarifasSedePage                  = () => import('@/pages/TarifasSedePage.vue')
const ClientesPage                 = () => import('@/pages/ClientesPage.vue')
const ReservasPage                 = () => import('@/pages/ReservasPage.vue')
const TarifasNegocioPage           = () => import('@/pages/TarifasNegocio.vue')

const routes = [
  { path: '/login', name: 'login', component: LoginPage, meta: { public: true } },

  // ── Dashboard ──────────────────────────────────────────────
  { path: '/', name: 'overview', component: OverviewPage, meta: { requiresAuth: true } },

  // ── Franquicias ────────────────────────────────────────────
  {
    path: '/franquicias',
    name: 'franquicias',
    component: FranquiciasPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/franquicias/:uuid/colaboradores',
    name: 'colaboradores-franquicia',
    component: ColaboradoresFranquiciaPage,
    meta: { requiresAuth: true },
  },

  // ── Negocios ───────────────────────────────────────────────
  {
    path: '/negocios',
    name: 'negocios',
    component: NegociosPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/negocios/:nit/colaboradores',
    name: 'colaboradores-negocio',
    component: ColaboradoresNegocioPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/negocios/:nit/tarifas',
    name: 'tarifas-negocio',
    component: TarifasNegocioPage,
    meta: { requiresAuth: true },
  },

  // ── Sedes (menú sidebar) ───────────────────────────────────
  {
    path: '/sedes',
    name: 'sedes-general',
    component: SedesGeneralPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/sedes/:uuid/colaboradores',
    name: 'colaboradores-sede',
    component: ColaboradoresSedePage,
    meta: { requiresAuth: true },
  },

  // ── Sedes (parametrización interna: pisos, puestos, tarifas)
  // Se llega desde SedesGeneralPage → "Puestos" button
  {
    path: '/sedes/:sede/puestos',
    name: 'puestos',
    component: PuestosSedePage,
    meta: { requiresAuth: true },
  },

  // ── Tarifas ────────────────────────────────────────────
  {
    path: '/negocios/:nit/sedes/:sede/tarifas',
    name: 'tarifas',
    component: TarifasSedePage,
    meta: { requiresAuth: true },
  },
  {
    path: '/sedes/:sede/tarifas',
    name: 'tarifas',
    component: TarifasSedePage,
    meta: { requiresAuth: true },
  },

  // ── Operaciones ────────────────────────────────────────────
  {
    path: '/clientes',
    name: 'clientes',
    component: ClientesPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/reservas',
    name: 'reservas',
    component: ReservasPage,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// Guarda global
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) return { name: 'login' }
  if (to.name === 'login' && auth.isAuthenticated)   return { name: 'overview' }
})

export default router
