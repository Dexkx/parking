
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_NOMINATION_API,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default api

export const search = async (query) => {
  const rs = await api.get('/search', {
    params: {
      q: query,
      format: 'jsonv2',
    },
  })
  return rs.data
}

export const reverse = async (query) => {
  const rs = await api.get('/reverse', {
    params: {
      lat: query.lat,
      lon: query.lon,
      format: 'jsonv2',
    },
  })
  return rs.data
}
