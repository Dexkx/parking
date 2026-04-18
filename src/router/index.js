import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const LoginPage       = () => import('@/pages/LoginPage.vue')
const OverviewPage    = () => import('@/pages/OverviewPage.vue')
const FranquiciasPage = () => import('@/pages/FranquiciasPage.vue')
const NegociosPage    = () => import('@/pages/NegociosPage.vue')
const SedesPage       = () => import('@/pages/SedesPage.vue')
const PuestosPage     = () => import('@/pages/PuestosPage.vue')
const TarifasPage     = () => import('@/pages/TarifasPage.vue')
const ClientesPage    = () => import('@/pages/ClientesPage.vue')
const ReservasPage    = () => import('@/pages/ReservasPage.vue')

const routes = [
  { path: '/login', name: 'login', component: LoginPage, meta: { public: true } },
  { path: '/',                          name: 'overview',    component: OverviewPage,    meta: { requiresAuth: true } },
  { path: '/franquicias',               name: 'franquicias', component: FranquiciasPage, meta: { requiresAuth: true } },
  { path: '/negocios',                  name: 'negocios',    component: NegociosPage,    meta: { requiresAuth: true } },
  { path: '/negocios/:nit/sedes',       name: 'sedes',       component: SedesPage,       meta: { requiresAuth: true } },
  { path: '/negocios/:nit/sedes/:sede', name: 'puestos',     component: PuestosPage,     meta: { requiresAuth: true } },
  { path: '/negocios/:nit/sedes/:sede/tarifas', name: 'tarifas', component: TarifasPage, meta: { requiresAuth: true } },
  { path: '/clientes',                  name: 'clientes',    component: ClientesPage,    meta: { requiresAuth: true } },
  { path: '/reservas',                  name: 'reservas',    component: ReservasPage,    meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) return { name: 'login' }
  if (to.name === 'login' && auth.isAuthenticated) return { name: 'overview' }
})

export default router
