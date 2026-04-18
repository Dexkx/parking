import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('access_token')

  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

api.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post('/api/token/refresh', { refresh })
          localStorage.setItem('access_token', data.access)
          original.headers.Authorization = `Bearer ${data.access}`
          return api(original)
        } catch {
          localStorage.clear()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(err)
  }
)

export default api

// ── Auth ──────────────────────────────────────────────────────
export const authApi = {
  login:    (d) => api.post('/token', d),
  refresh:  (r) => api.post('/token/refresh', { refresh: r }),
  me:       (id) => api.get(`/usuarios/${id}`),
}

// ── Franquicias ───────────────────────────────────────────────
export const franquiciasApi = {
  list:              ()        => api.get('/franquicias'),
  create:            (d)       => api.post('/franquicias', d),
  update:            (id, d)   => api.patch(`/franquicias/${id}`, d),
  remove:            (id)      => api.delete(`/franquicias/${id}`),
  colaboradores:     (id)      => api.get(`/franquicias/${id}/colaboradores`),
  addColaborador:    (id, d)   => api.post(`/franquicias/${id}/colaboradores`, d),
  negocios:          (id)      => api.get(`/franquicias/${id}/negocios`),
  addNegocio:        (id, d)   => api.post(`/franquicias/${id}/negocios`, d),
}

// ── Negocios ──────────────────────────────────────────────────
export const negociosApi = {
  list:              (p = {})  => api.get('/negocios', { params: p }),
  create:            (d)       => api.post('/negocios', d),
  update:            (nit, d)  => api.patch(`/negocios/${nit}`, d),
  remove:            (nit)     => api.delete(`/negocios/${nit}`),
  colaboradores:     (nit)     => api.get(`/negocios/${nit}/colaboradores`),
  addColaborador:    (nit, d)  => api.post(`/negocios/${nit}/colaboradores`, d),
  editColaborador:   (nit, id, d)  => api.patch(`/negocios/${nit}/colaboradores/${id}`, d),
}

// ── Sedes ─────────────────────────────────────────────────────
export const sedesApi = {
  list:    (nit)        => api.get(`/negocios/${nit}/sedes`),
  create:  (nit, d)     => api.post(`/negocios/${nit}/sedes`, d),
  update:  (nit, id, d) => api.patch(`/negocios/${nit}/sedes/${id}`, d),
  remove:  (nit, id)    => api.delete(`/negocios/${nit}/sedes/${id}`),
}

// ── Puestos ───────────────────────────────────────────────────
export const puestosApi = {
  list:   (nit, sedeId)        => api.get(`/negocios/${nit}/sedes/${sedeId}/puestos`),
  create: (nit, sedeId, d)     => api.post(`/negocios/${nit}/sedes/${sedeId}/puestos`, d),
  update: (nit, sedeId, pk, d) => api.patch(`/negocios/${nit}/sedes/${sedeId}/puestos/${pk}`, d),
  remove: (nit, sedeId, pk)    => api.delete(`/negocios/${nit}/sedes/${sedeId}/puestos/${pk}`),
}

// ── Tarifas ───────────────────────────────────────────────────
export const tarifasApi = {
  list:   (nit, sedeId)        => api.get(`/negocios/${nit}/sedes/${sedeId}/tarifas`),
  create: (nit, sedeId, d)     => api.post(`/negocios/${nit}/sedes/${sedeId}/tarifas`, d),
  update: (nit, sedeId, pk, d) => api.patch(`/negocios/${nit}/sedes/${sedeId}/tarifas/${pk}`, d),
  remove: (nit, sedeId, pk)    => api.delete(`/negocios/${nit}/sedes/${sedeId}/tarifas/${pk}`),
}

// ── Clientes ──────────────────────────────────────────────────
export const clientesApi = {
  list:   (nit)     => api.get(`/negocios/${nit}/clientes`),
  create: (nit, d)  => api.post(`/negocios/${nit}/clientes`, d),
  remove: (nit, id) => api.delete(`/negocios/${nit}/clientes/${id}`),
}

// ── Reservas ──────────────────────────────────────────────────
export const reservasApi = {
  list:    (nit, p = {}) => api.get(`/negocios/${nit}/reservas`, { params: p }),
  create:  (nit, d)      => api.post(`/negocios/${nit}/reservas`, d),
  cancelar:(nit, uuid)   => api.delete(`/negocios/${nit}/reservas/${uuid}`),
}

// ── Catálogos ─────────────────────────────────────────────────
export const catalogosApi = {
  tiposVehiculo: () => api.get('/tipos-vehiculos'),
  tiposColaborador: () => api.get('/tipos-colaborador'),
  paises:        () => api.get('/countries'),
  departamentos: (paisId) => api.get(`/countries/${paisId}/states`),
  ciudades:      (paisId, stateId) => api.get(`/countries/${paisId}/states/${stateId}/cities`),
}
