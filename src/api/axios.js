import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// ── Request: inyectar token JWT ──
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('access_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// ── Response: refresh automático ──
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

// ── Response: auditoria errores ──
api.interceptors.response.use(
  res => {
    console.log(res)
    return res
  },
  err => {
    console.log(err)
    return Promise.reject(err)
  }
)


export default api

// ── Endpoints helpers ──
export const authApi = {
  login: (data) => api.post('/token', data),
  refresh: (refresh) => api.post('/token/refresh', { refresh }),
  register: (data) => api.post('/usuarios', data),
  me: (id) => api.get(`/usuarios/${id}`),
}

export const negociosApi = {
  list: (params) => api.get('/negocios', { params }),
  detail: (nit) => api.get(`/negocios/${nit}`),
  resenas: (nit) => api.get(`/negocios/${nit}/resenas`),
  crearResena: (nit, data) => api.post(`/negocios/${nit}/resenas`, data),
  tarifas: (nit) => api.get(`/negocios/${nit}/tarifas`),
  puestos: (nit) => api.get(`/negocios/${nit}/puestos`),
}

export const reservasApi = {
  mis: (nit) => api.get(`/negocios/${nit}/reservas`),
  crear: (nit, data) => api.post(`/negocios/${nit}/reservas`, data),
  cancelar: (nit, uuid) => api.delete(`/negocios/${nit}/reservas/${uuid}`),
}

export const vehiculosApi = {
  list: (userId) => api.get(`/usuarios/${userId}/vehiculos`),
  crear: (userId, data) => api.post(`/usuarios/${userId}/vehiculos`, data),
}

export const catalogosApi = {
  ciudades: (paisId) => api.get(`/paises/${paisId}/ciudades`),
  tiposVehiculo: () => api.get('/tipos-vehiculos'),
}
