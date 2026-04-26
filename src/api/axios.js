import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'


const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use(cfg => {
  const auth = useAuthStore()
  const token = auth.getAccessToken

  if (token) cfg.headers.Authorization = `Bearer ${token}`

  return cfg
})

api.interceptors.response.use(
  res => res,
  async err => {
    // Evitar crash si no hay respuesta del servidor
    if (!err.response) return Promise.reject(err)

    const auth = useAuthStore()
    const original = err.config

    const sessionInvalid = err.response.data.code === "token_not_valid"
    // Si el error es 401 (o token_not_valid), intentamos renovar
    const sessionExpired = err.response.status === 401 || err.response.data?.code === "token_not_valid"

    if (sessionExpired && !original._retry) {
      original._retry = true

      const tokenRefresh = auth.getRefreshToken
      if (tokenRefresh) {
        try {
          const { data } = await axios.post('/api/token/refresh', { refresh: tokenRefresh })
          auth.setAccessToken(data.access)
          original.headers.Authorization = `Bearer ${data.access}`
          return api(original)
        } catch (error) {
          console.log(error, error.response)
        }
      }
    }

    if (sessionInvalid) {
      const router = useRouter()
      auth.logout()
      router.push('/login')
    }
    return Promise.reject(err)
  }
)

export default api

// ── Auth ──────────────────────────────────────────────────────
export const authApi = {
  login:   (d)  => api.post('/token/dashboard', d),
  refresh: (r)  => api.post('/token/refresh', { refresh: r }),
  me:      (id) => api.get(`/usuarios/${id}`),
}

// ── Franquicias ───────────────────────────────────────────────
export const franquiciasApi = {
  list:                ()           => api.get('/franquicias'),
  get:                 (uuid)       => api.get(`/franquicias/${uuid}`),
  create:              (d)          => api.post('/franquicias', d),
  update:              (id, d)      => api.patch(`/franquicias/${id}`, d),
  editStatus:          (id, newStatus) => api.patch(`/franquicias/${id}`, { 'status': newStatus }),
  // remove:              (id)         => api.delete(`/franquicias/${id}`),

  // Colaboradores de la franquicia
  colaboradores:       (id)         => api.get(`/franquicias/${id}/colaboradores`),
  addColaborador:      (id, d)      => api.post(`/franquicias/${id}/colaboradores`, d),
  editColaborador:     (id, uid, d) => api.patch(`/franquicias/${id}/colaboradores/${uid}`, d),
  removeColaborador:   (id, uid)    => api.delete(`/franquicias/${id}/colaboradores/${uid}`),
}

// ── Negocios ──────────────────────────────────────────────────
export const negociosApi = {
  list:                (p = {})     => api.get('/negocios', { params: p }),
  get:                 (nit)        => api.get(`/negocios/${nit}`),
  create:              (d)          => api.post('/negocios', d),
  update:              (nit, d)     => api.patch(`/negocios/${nit}`, d),
  editStatus:          (nit, newStatus) => api.patch(`/negocios/${nit}`, { 'status': newStatus }),
  // remove:              (nit)        => api.delete(`/negocios/${nit}`),

  // Colaboradores del negocio
  colaboradores:       (nit)        => api.get(`/negocios/${nit}/colaboradores`),
  addColaborador:      (nit, d)     => api.post(`/negocios/${nit}/colaboradores`, d),
  editColaborador:     (nit, uid, d)=> api.patch(`/negocios/${nit}/colaboradores/${uid}`, d),
  removeColaborador:   (nit, uid)   => api.delete(`/negocios/${nit}/colaboradores/${uid}`),
}
// ── Tarifas ───────────────────────────────────────────────────
export const tarifasNegocioApi = {
  list:   (nit)         => api.get(`/negocios/${nit}/tarifas`),
  create: (nit, d)      => api.post(`/negocios/${nit}/tarifas`, d),
  update: (nit, pk, d)  => api.patch(`/negocios/${nit}/tarifas/${pk}`, d),
  editStatus: (nit, pk, newStatus) => api.patch(`/negocios/${nit}/tarifas/${pk}`, { 'status': newStatus }),
}

// ── Sedes ─────────────────────────────────────────────────────
export const sedesApi = {
  list:   ()           => api.get(`/sedes`),
  get:    (id)         => api.get(`/sedes/${id}`),
  create: (d)          => api.post(`/sedes`, d),
  update: (id, d)      => api.patch(`/sedes/${id}`, d),
  editStatus: (id, newStatus) => api.patch(`/sedes/${id}`, { 'status': newStatus }),

  // Colaboradores de la sede
  colaboradores:       (id)        => api.get(`/sedes/${id}/colaboradores`),
  addColaborador:      (id, d)     => api.post(`/sedes/${id}/colaboradores`, d),
  editColaborador:     (id, uid, d)=> api.patch(`/sedes/${id}/colaboradores/${uid}`, d),
  removeColaborador:   (id, uid)   => api.delete(`/sedes/${id}/colaboradores/${uid}`),
}

// ── Puestos ───────────────────────────────────────────────────
export const puestosSedeApi = {
  list:   (sid)         => api.get(`/sedes/${sid}/puestos`),
  create: (sid, d)      => api.post(`/sedes/${sid}/puestos`, d),
  update: (sid, pk, d)  => api.patch(`/sedes/${sid}/puestos/${pk}`, d),
  editStatus: (sid, piso, numero, tipo_vehiculo, newStatus) => api.patch(`/sedes/${sid}/puestos/${piso}/${numero}/${tipo_vehiculo}`, { 'status': newStatus }),
}

// ── Tarifas ───────────────────────────────────────────────────
export const tarifasSedeApi = {
  list:   (sid)         => api.get(`/sedes/${sid}/tarifas`),
  create: (sid, d)      => api.post(`/sedes/${sid}/tarifas`, d),
  update: (sid, pk, d)  => api.patch(`/sedes/${sid}/tarifas/${pk}`, d),
  editStatus: (sid, pk, newStatus) => api.patch(`/sedes/${sid}/tarifas/${pk}`, { 'status': newStatus }),
}

// ── Clientes ──────────────────────────────────────────────────
export const clientesApi = {
  list:   (nit)      => api.get(`/negocios/${nit}/clientes`),
  create: (nit, d)   => api.post(`/negocios/${nit}/clientes`, d),
  editStatus: (nit, uid, newStatus) => api.patch(`/negocios/${nit}/clientes/${uid}`, { 'status': newStatus }),
  delete: (nit, uid) => api.delete(`/negocios/${nit}/clientes/${uid}`),
}

// ── Reservas ──────────────────────────────────────────────────
export const reservasApi = {
  list:    (p = {}) => api.get(`/reservas`, { params: p }),
  create:  (d)      => api.post(`/reservas`, d),
  cancelar:(uuid)   => api.patch(`/reservas/${uuid}`, { 'status': 'Cancelado' }),
  finalizar:(uuid)   => api.patch(`/reservas/${uuid}`, { 'status': 'Completado' }),
}

// ── Catálogos ─────────────────────────────────────────────────
export const catalogosApi = {
  tiposVehiculo:    ()            => api.get('/tipos-vehiculos?status=Activo'),
  tiposColaborador: ()            => api.get('/tipos-colaborador?status=Activo'),
  paises:           ()            => api.get('/countries'),
  departamentos:    (paisId)      => api.get(`/countries/${paisId}/states`),
  ciudades:         (paisId, stateId)      => api.get(`/countries/${paisId}/states/${stateId}/cities`),
}
