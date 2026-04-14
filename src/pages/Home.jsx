import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Search, MapPin, Zap, Shield, Star } from 'lucide-react'
import MapView from '../components/MapView'
import { negociosApi } from '../api/axios'

const S = {
  hero: {
    minHeight: 'calc(100vh - 64px)',
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 0,
    position: 'relative',
    overflow: 'hidden',
  },
  left: {
    display: 'flex', flexDirection: 'column',
    justifyContent: 'center', padding: '4rem 3rem 4rem 5rem',
    position: 'relative', zIndex: 1,
  },
  eyebrow: {
    display: 'inline-flex', alignItems: 'center', gap: 6,
    padding: '5px 12px', borderRadius: 100,
    background: 'var(--accent-dim)', border: '1px solid rgba(0,229,176,0.25)',
    color: 'var(--accent)', fontSize: 12, fontWeight: 600,
    letterSpacing: '0.08em', marginBottom: '1.5rem',
    width: 'fit-content',
  },
  title: {
    fontFamily: 'var(--font-head)', fontWeight: 800,
    fontSize: 'clamp(40px, 5vw, 62px)',
    lineHeight: 1.05, letterSpacing: '-2px',
    color: 'var(--text-primary)', marginBottom: '1.25rem',
  },
  accent: { color: 'var(--accent)' },
  sub: {
    fontSize: 16, color: 'var(--text-secondary)',
    lineHeight: 1.7, maxWidth: 400, marginBottom: '2.5rem',
  },
  searchBar: {
    display: 'flex', gap: 10, alignItems: 'center',
    background: 'var(--bg-card)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)', padding: '6px 6px 6px 16px',
    maxWidth: 500,
  },
  searchInput: {
    flex: 1, background: 'none', border: 'none',
    color: 'var(--text-primary)', fontSize: 15, outline: 'none',
    fontFamily: 'var(--font-body)',
  },
  searchBtn: {
    display: 'flex', alignItems: 'center', gap: 6,
    padding: '10px 20px', borderRadius: 'var(--radius-md)',
    background: 'var(--accent)', border: 'none',
    color: '#000', fontFamily: 'var(--font-head)',
    fontWeight: 700, fontSize: 14, cursor: 'pointer',
    whiteSpace: 'nowrap', transition: 'opacity .2s',
  },
  stats: {
    display: 'flex', gap: '2rem', marginTop: '2.5rem',
  },
  statItem: {
    display: 'flex', flexDirection: 'column', gap: 2,
  },
  statNum: {
    fontFamily: 'var(--font-head)', fontWeight: 800,
    fontSize: 28, color: 'var(--text-primary)', letterSpacing: '-1px',
  },
  statLabel: { fontSize: 12, color: 'var(--text-muted)', fontWeight: 500 },
  mapPanel: { position: 'relative' },
  mapGrad: {
    position: 'absolute', left: 0, top: 0, bottom: 0, width: 80,
    background: 'linear-gradient(to right, var(--bg-base), transparent)',
    zIndex: 10, pointerEvents: 'none',
  },
  features: {
    padding: '5rem 5rem',
    background: 'var(--bg-surface)',
    borderTop: '1px solid var(--border)',
  },
  featTitle: {
    fontFamily: 'var(--font-head)', fontWeight: 800,
    fontSize: 36, color: 'var(--text-primary)',
    letterSpacing: '-1px', marginBottom: '0.5rem',
  },
  featGrid: {
    display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 20, marginTop: '3rem',
  },
  featCard: {
    padding: '1.5rem',
    background: 'var(--bg-card)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
  },
  featIcon: {
    width: 44, height: 44, borderRadius: 'var(--radius-sm)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    marginBottom: '1rem',
  },
}

const FEATURES = [
  { icon: <MapPin size={20} />, color: '#00e5b0', bg: 'rgba(0,229,176,0.1)', title: 'Mapa en tiempo real', desc: 'Visualiza todos los parqueaderos disponibles en tu ciudad con disponibilidad actualizada.' },
  { icon: <Zap size={20} />, color: '#4f8ef7', bg: 'rgba(79,142,247,0.1)', title: 'Reserva en segundos', desc: 'Selecciona tu espacio, elige la duración y confirma. Tu puesto queda asegurado.' },
  { icon: <Shield size={20} />, color: '#fbbf24', bg: 'rgba(251,191,36,0.1)', title: 'Pago seguro', desc: 'Múltiples métodos de pago con cifrado de extremo a extremo. Tu dinero, seguro.' },
]

export default function Home({ onLoginOpen }) {
  const [query, setQuery] = useState('')
  const [negocios, setNegocios] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    negociosApi.list().then(r => setNegocios(r.data?.results ?? r.data ?? [])).catch(() => {})
  }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    navigate(`/resultados?q=${encodeURIComponent(query)}`)
  }

  return (
    <>
      {/* Hero */}
      <section style={S.hero}>
        {/* Left */}
        <div style={S.left}>
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <div style={S.eyebrow}>
              <Star size={12} fill="currentColor" />
              La plataforma #1 de parqueaderos en Colombia
            </div>
            <h1 style={S.title}>
              Tu parqueadero<br />
              <span style={S.accent}>perfecto,</span><br />
              en segundos.
            </h1>
            <p style={S.sub}>
              Encuentra, reserva y paga tu espacio de parqueo desde la app.
              Sin filas. Sin complicaciones.
            </p>

            <form onSubmit={handleSearch}>
              <div style={S.searchBar}>
                <Search size={16} color="var(--text-muted)" />
                <input
                  style={S.searchInput}
                  placeholder="Ciudad, barrio o nombre..."
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                />
                <button type="submit" style={S.searchBtn}>
                  <Search size={14} /> Buscar
                </button>
              </div>
            </form>

            <div style={S.stats}>
              {[
                { num: negocios.length || '150+', label: 'Parqueaderos' },
                { num: '12K+', label: 'Usuarios' },
                { num: '4.8★', label: 'Valoración' },
              ].map(({ num, label }) => (
                <div key={label} style={S.statItem}>
                  <span style={S.statNum}>{num}</span>
                  <span style={S.statLabel}>{label}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Map panel */}
        <div style={S.mapPanel}>
          <div style={S.mapGrad} />
          <MapView negocios={negocios} />
        </div>
      </section>

      {/* Features */}
      <section style={S.features}>
        <motion.div
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: 0.5 }}
        >
          <p style={{ fontSize: 12, color: 'var(--accent)', fontWeight: 600, letterSpacing: '0.1em', marginBottom: 8 }}>
            ¿POR QUÉ PARKAPP?
          </p>
          <h2 style={S.featTitle}>Todo lo que necesitas</h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: 460 }}>
            Diseñado para conductores colombianos que valoran su tiempo.
          </p>
        </motion.div>

        <div style={S.featGrid}>
          {FEATURES.map((f, i) => (
            <motion.div key={f.title} style={S.featCard}
              initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }} transition={{ delay: i * 0.1 }}
              whileHover={{ borderColor: 'var(--border-hover)', y: -2 }}
            >
              <div style={{ ...S.featIcon, background: f.bg, color: f.color }}>
                {f.icon}
              </div>
              <div style={{ fontFamily: 'var(--font-head)', fontWeight: 700, fontSize: 16, marginBottom: 8 }}>
                {f.title}
              </div>
              <div style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {f.desc}
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </>
  )
}
