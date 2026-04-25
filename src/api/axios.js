import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// ── Inyectar token en cada request ──
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('access_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// ── Refresh silencioso al expirar el token ──
api.interceptors.response.use(
  res => res,
  async err => {
    console.log(err.response)
    const original = err.config
    const code_status = [401, 403]
    if (code_status.includes(err.response?.status) && !original._retry) {
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
          window.location.href = '/'
        }
      }
    }
    return Promise.reject(err)
  }
)

export default api

// ─────────────────────────────────────────
// Helpers por módulo (mapean los endpoints del backend Django)
// ─────────────────────────────────────────

export const authApi = {
  /** POST /api/token  → { access, refresh } */
  login: (data)           => api.post('/token', data),
  /** POST /api/token/refresh */
  refresh: (refresh)      => api.post('/token/refresh', { refresh }),
  /** POST /api/usuarios  → crear cuenta */
  register: (data)        => api.post('/usuarios', data),
  /** GET  /api/usuarios/:id */
  me: (id)                => api.get(`/usuarios/${id}`),
}

export const sedesApi = {
  /** GET  /api/sedes?search=&status= */
  list: (params = {})     => api.get('/sedes-publicas', { params }),
  /** GET  /api/sedes/:id */
  detail: (id)           => api.get(`/sedes-publicas/${id}`),
  /** GET  /api/sedes/:id/resenas */
  resenas: (id)          => api.get(`/sedes-publicas/${id}/resenas`),
  /** POST /api/sedes/:id/resenas */
  crearResena: (id, d)   => api.post(`/sedes/${id}/resenas`, d),
  /** GET  /api/sedes/:id/tarifas */
  tarifas: (id)          => api.get(`/sedes-publicas/${id}/tarifas`),
  /** GET  /api/sedes/:id/puestos */
  puestos: (id)          => api.get(`/sedes/${id}/puestos`),
}

export const reservasApi = {
  /** GET  /api/sedes/:uuid/reservas */
  mis: (id)              => api.get(`/usuarios/${id}/reservas`),
  /** POST /api/sedes/:uuid/reservas */
  crear: (id, d)         => api.post(`/usuarios/${id}/reservas`, d),
  /** PATCH /api/sedes/:uuid/reservas/:uuid */
  cancelar: (id, r_uuid)   => api.patch(`/usuarios/${id}/reservas/${r_uuid}`, { status: 'Cancelado' }),
}

export const vehiculosApi = {
  /** GET  /api/usuarios/:id/vehiculos */
  list: (uid)             => api.get(`/usuarios/${uid}/vehiculos`),
  /** POST /api/usuarios/:id/vehiculos */
  crear: (uid, d)         => api.post(`/usuarios/${uid}/vehiculos`, d),
}

export const catalogosApi = {
  tiposVehiculo: ()       => api.get('/tipos-vehiculos'),
  paises: ()              => api.get('/paises'),
  ciudades: (paisId)      => api.get(`/paises/${paisId}/ciudades`),
}
