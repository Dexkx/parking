import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, SlidersHorizontal, MapIcon, LayoutGrid, Loader2 } from 'lucide-react'
import ParkCard from '../components/ParkCard'
import MapView from '../components/MapView'
import { negociosApi } from '../api/axios'

const S = {
  page: { display: 'flex', height: 'calc(100vh - 64px)', overflow: 'hidden' },
  sidebar: {
    width: 420, flexShrink: 0,
    display: 'flex', flexDirection: 'column',
    borderRight: '1px solid var(--border)',
    overflow: 'hidden',
  },
  sidebarHead: {
    padding: '1.25rem 1.25rem 0',
    borderBottom: '1px solid var(--border)',
    paddingBottom: '1rem',
  },
  pageTitle: {
    fontFamily: 'var(--font-head)', fontWeight: 800, fontSize: 20,
    color: 'var(--text-primary)', marginBottom: '0.75rem',
  },
  searchRow: {
    display: 'flex', gap: 8, alignItems: 'center',
    background: 'var(--bg-input)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)', padding: '8px 12px',
  },
  searchInput: {
    flex: 1, background: 'none', border: 'none',
    color: 'var(--text-primary)', fontSize: 13,
    outline: 'none', fontFamily: 'var(--font-body)',
  },
  filterRow: {
    display: 'flex', gap: 6, padding: '0.75rem 1.25rem',
    overflowX: 'auto', borderBottom: '1px solid var(--border)',
  },
  filterChip: (active) => ({
    padding: '5px 12px', borderRadius: 100, fontSize: 12,
    fontWeight: 500, whiteSpace: 'nowrap', cursor: 'pointer',
    border: '1px solid',
    background: active ? 'var(--accent-dim)' : 'transparent',
    borderColor: active ? 'var(--accent)' : 'var(--border)',
    color: active ? 'var(--accent)' : 'var(--text-secondary)',
    transition: 'all .15s',
  }),
  listWrap: { flex: 1, overflowY: 'auto', padding: '1rem 1.25rem' },
  count: { fontSize: 12, color: 'var(--text-muted)', marginBottom: '0.75rem' },
  grid: { display: 'flex', flexDirection: 'column', gap: 12 },
  mapWrap: { flex: 1 },
  emptyState: {
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    justifyContent: 'center', height: 200,
    color: 'var(--text-muted)', gap: 8, textAlign: 'center',
  },
  skeletonCard: {
    height: 180, borderRadius: 'var(--radius-lg)',
    background: 'linear-gradient(90deg, var(--bg-card) 25%, var(--bg-card-hover) 50%, var(--bg-card) 75%)',
    backgroundSize: '800px 100%',
    animation: 'shimmer 1.4s infinite',
  },
}

const FILTERS = [
  { key: 'all', label: 'Todos' },
  { key: 'disponible', label: 'Disponibles' },
  { key: 'mejor_valorado', label: 'Mejor valorados' },
  { key: 'mas_cercano', label: 'Más cercanos' },
]

export default function Resultados({ onLoginRequired }) {
  const [searchParams] = useSearchParams()
  const [negocios, setNegocios] = useState([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState(searchParams.get('q') || '')
  const [filter, setFilter] = useState('all')
  const [view, setView] = useState('split') // 'split' | 'list' | 'map'

  const fetchNegocios = useCallback(async () => {
    setLoading(true)
    try {
      const params = {}
      if (query) params.search = query
      if (filter === 'disponible') params.status = 'Activo'
      const res = await negociosApi.list(params)
      let data = res.data?.results ?? res.data ?? []
      if (filter === 'mejor_valorado') data = [...data].sort((a, b) => (b.puntuacion || 0) - (a.puntuacion || 0))
      setNegocios(data)
    } catch {
      setNegocios([])
    } finally { setLoading(false) }
  }, [query, filter])

  useEffect(() => { fetchNegocios() }, [fetchNegocios])

  const showMap = view !== 'list'
  const showList = view !== 'map'

  return (
    <div style={S.page}>
      {/* Sidebar lista */}
      {showList && (
        <div style={S.sidebar}>
          {/* Header */}
          <div style={S.sidebarHead}>
            <div style={S.pageTitle}>Parqueaderos</div>
            <div style={S.searchRow}>
              <Search size={14} color="var(--text-muted)" />
              <input
                style={S.searchInput}
                placeholder="Buscar por nombre o dirección..."
                value={query}
                onChange={e => setQuery(e.target.value)}
              />
              {loading && <Loader2 size={14} color="var(--text-muted)" style={{ animation: 'spin 1s linear infinite' }} />}
            </div>
          </div>

          {/* Filtros */}
          <div style={S.filterRow}>
            {FILTERS.map(f => (
              <button key={f.key} style={S.filterChip(filter === f.key)} onClick={() => setFilter(f.key)}>
                {f.label}
              </button>
            ))}
          </div>

          {/* Lista */}
          <div style={S.listWrap}>
            <div style={S.count}>{negocios.length} resultado{negocios.length !== 1 ? 's' : ''}</div>

            {loading ? (
              <div style={S.grid}>
                {[1, 2, 3].map(i => <div key={i} style={S.skeletonCard} />)}
              </div>
            ) : negocios.length === 0 ? (
              <div style={S.emptyState}>
                <Search size={32} strokeWidth={1} />
                <div style={{ fontFamily: 'var(--font-head)', fontWeight: 700 }}>Sin resultados</div>
                <div style={{ fontSize: 13 }}>Intenta con otra ciudad o elimina los filtros</div>
              </div>
            ) : (
              <div style={S.grid}>
                <AnimatePresence>
                  {negocios.map((neg, i) => (
                    <ParkCard key={neg.nit} negocio={neg} index={i} onLoginRequired={onLoginRequired} />
                  ))}
                </AnimatePresence>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Mapa */}
      {showMap && (
        <div style={S.mapWrap}>
          <MapView negocios={negocios} />
        </div>
      )}
    </div>
  )
}
