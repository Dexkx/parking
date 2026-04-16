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

export const negociosApi = {
  /** GET  /api/negocios?search=&status= */
  list: (params = {})     => api.get('/negocios', { params }),
  /** GET  /api/negocios/:nit */
  detail: (nit)           => api.get(`/negocios/${nit}`),
  /** GET  /api/negocios/:nit/resenas */
  resenas: (nit)          => api.get(`/negocios/${nit}/resenas`),
  /** POST /api/negocios/:nit/resenas */
  crearResena: (nit, d)   => api.post(`/negocios/${nit}/resenas`, d),
  /** GET  /api/negocios/:nit/tarifas */
  tarifas: (nit)          => api.get(`/negocios/${nit}/tarifas`),
  /** GET  /api/negocios/:nit/puestos */
  puestos: (nit)          => api.get(`/negocios/${nit}/puestos`),
}

export const reservasApi = {
  /** GET  /api/negocios/:nit/reservas */
  mis: (nit)              => api.get(`/negocios/${nit}/reservas`),
  /** POST /api/negocios/:nit/reservas */
  crear: (nit, d)         => api.post(`/negocios/${nit}/reservas`, d),
  /** DELETE /api/negocios/:nit/reservas/:uuid */
  cancelar: (nit, uuid)   => api.delete(`/negocios/${nit}/reservas/${uuid}`),
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
