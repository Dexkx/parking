import { useState } from 'react'
import { motion } from 'framer-motion'
import { MapPin, Star, Clock, Car, ChevronRight, DollarSign, Users } from 'lucide-react'
import Swal from 'sweetalert2'
import { useAuth } from '../context/AuthContext'
import { reservasApi } from '../api/axios'
import { toast } from 'react-toastify'

const S = {
  card: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    overflow: 'hidden',
    cursor: 'pointer',
    transition: 'all .25s',
    display: 'flex', flexDirection: 'column',
  },
  badge: (color) => ({
    display: 'inline-flex', alignItems: 'center', gap: 4,
    padding: '3px 8px', borderRadius: 100,
    fontSize: 11, fontWeight: 600, letterSpacing: '0.04em',
    background: color === 'green' ? 'rgba(0,229,176,0.12)' : 'rgba(255,77,109,0.12)',
    color: color === 'green' ? 'var(--accent)' : 'var(--danger)',
    border: `1px solid ${color === 'green' ? 'rgba(0,229,176,0.25)' : 'rgba(255,77,109,0.25)'}`,
  }),
  topBar: {
    padding: '1rem 1rem 0',
    display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
  },
  nombre: {
    fontFamily: 'var(--font-head)', fontWeight: 700, fontSize: 16,
    color: 'var(--text-primary)', lineHeight: 1.2, marginBottom: 4,
  },
  dir: {
    display: 'flex', alignItems: 'center', gap: 4,
    fontSize: 12, color: 'var(--text-secondary)',
  },
  divider: { height: 1, background: 'var(--border)', margin: '0.75rem 1rem' },
  stats: {
    padding: '0 1rem', display: 'grid',
    gridTemplateColumns: '1fr 1fr 1fr', gap: 8,
  },
  stat: {
    display: 'flex', flexDirection: 'column', gap: 2,
    padding: '8px', borderRadius: 'var(--radius-sm)',
    background: 'var(--bg-input)',
  },
  statLabel: { fontSize: 10, color: 'var(--text-muted)', fontWeight: 500 },
  statVal: { fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-head)' },
  footer: {
    padding: '0.75rem 1rem',
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
  },
  stars: { display: 'flex', alignItems: 'center', gap: 3 },
  reservarBtn: {
    display: 'flex', alignItems: 'center', gap: 6,
    padding: '7px 14px', borderRadius: 'var(--radius-sm)',
    background: 'var(--accent)', border: 'none',
    color: '#000', fontFamily: 'var(--font-head)',
    fontWeight: 700, fontSize: 13, cursor: 'pointer',
    transition: 'all .2s',
  },
}

function Stars({ val }) {
  const n = Math.round(val || 0)
  return (
    <div style={S.stars}>
      {[1, 2, 3, 4, 5].map(i => (
        <Star key={i} size={12}
          fill={i <= n ? '#fbbf24' : 'none'}
          color={i <= n ? '#fbbf24' : 'var(--text-muted)'}
          strokeWidth={1.5}
        />
      ))}
      <span style={{ fontSize: 12, color: 'var(--text-secondary)', marginLeft: 2 }}>
        {val ? Number(val).toFixed(1) : '—'}
      </span>
    </div>
  )
}

export default function ParkCard({ negocio, index = 0, onLoginRequired }) {
  const { isAuthenticated } = useAuth()
  const disponible = negocio.status === 'Activo'

  const handleReservar = async (e) => {
    e.stopPropagation()
    if (!isAuthenticated) { onLoginRequired(); return }
    if (!disponible) { toast.warning('Este parqueadero no está disponible'); return }

    const { isConfirmed, value } = await Swal.fire({
      title: `<span style="font-family:Syne;font-weight:800;font-size:20px;color:#eef0f5">${negocio.nombre}</span>`,
      html: `
        <div style="font-family:DM Sans;text-align:left;color:#8b92a8">
          <p style="margin-bottom:12px;color:#eef0f5">${negocio.direccion}</p>
          <label style="font-size:12px;font-weight:500;display:block;margin-bottom:6px">PLACA DEL VEHÍCULO</label>
          <input id="placa" placeholder="Ej: ABC123" maxlength="7"
            style="width:100%;padding:10px 14px;background:#1a1e2a;border:1px solid rgba(255,255,255,0.07);
            border-radius:8px;color:#eef0f5;font-size:14px;outline:none;font-family:DM Sans">
          <label style="font-size:12px;font-weight:500;display:block;margin:12px 0 6px">DURACIÓN</label>
          <select id="tiempo"
            style="width:100%;padding:10px 14px;background:#1a1e2a;border:1px solid rgba(255,255,255,0.07);
            border-radius:8px;color:#eef0f5;font-size:14px;font-family:DM Sans;outline:none">
            <option value="01:00:00">1 hora</option>
            <option value="02:00:00">2 horas</option>
            <option value="04:00:00">4 horas</option>
            <option value="08:00:00">8 horas</option>
          </select>
        </div>
      `,
      background: '#161922',
      showCancelButton: true,
      confirmButtonText: 'Confirmar reserva',
      cancelButtonText: 'Cancelar',
      confirmButtonColor: '#00e5b0',
      cancelButtonColor: '#374151',
      customClass: {
        popup: 'swal-dark-popup',
        confirmButton: 'swal-confirm',
      },
      preConfirm: () => ({
        placa: document.getElementById('placa').value.toUpperCase(),
        tiempo: document.getElementById('tiempo').value,
      })
    })

    if (!isConfirmed || !value.placa) return

    try {
      const now = new Date()
      const [h, m, s] = value.tiempo.split(':').map(Number)
      const end = new Date(now.getTime() + (h * 3600 + m * 60 + s) * 1000)

      await reservasApi.crear(negocio.nit, {
        piso: '1',
        numero: 1,
        tipo_vehiculo: 1,
        tiempo: value.tiempo,
        usuario: null, // el backend lo toma del token
        placa: value.placa,
        hf_inicio: now.toISOString(),
        hf_final: end.toISOString(),
      })

      await Swal.fire({
        icon: 'success',
        title: '<span style="font-family:Syne;color:#eef0f5">¡Reserva confirmada!</span>',
        html: `<span style="color:#8b92a8">Tu espacio en <b style="color:#00e5b0">${negocio.nombre}</b> está listo.</span>`,
        background: '#161922',
        confirmButtonColor: '#00e5b0',
        timer: 3000,
        timerProgressBar: true,
      })
    } catch {
      toast.error('No se pudo crear la reserva. Intenta de nuevo.')
    }
  }

  return (
    <motion.div
      style={S.card}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.07, type: 'spring', stiffness: 200, damping: 22 }}
      whileHover={{ y: -4, borderColor: 'var(--border-hover)', boxShadow: '0 12px 40px rgba(0,0,0,0.4)' }}
    >
      <div style={S.topBar}>
        <div style={{ flex: 1 }}>
          <div style={S.nombre}>{negocio.nombre}</div>
          <div style={S.dir}>
            <MapPin size={11} color="var(--accent)" />
            {negocio.direccion}
          </div>
        </div>
        <span style={S.badge(disponible ? 'green' : 'red')}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'currentColor', animation: disponible ? 'pulse-dot 1.5s infinite' : 'none' }} />
          {disponible ? 'Disponible' : 'Cerrado'}
        </span>
      </div>

      <div style={S.divider} />

      <div style={S.stats}>
        <div style={S.stat}>
          <span style={S.statLabel}>PRECIO/HORA</span>
          <span style={{ ...S.statVal, color: 'var(--accent)' }}>
            {negocio.tarifas?.[0]?.valor ? `$${Number(negocio.tarifas[0].valor).toLocaleString('es-CO')}` : '—'}
          </span>
        </div>
        <div style={S.stat}>
          <span style={S.statLabel}>PUESTOS</span>
          <span style={S.statVal}>{negocio.puestos_count ?? '—'}</span>
        </div>
        <div style={S.stat}>
          <span style={S.statLabel}>CIUDAD</span>
          <span style={{ ...S.statVal, fontSize: 12, color: 'var(--text-secondary)' }}>
            {negocio.ciudad?.name ?? '—'}
          </span>
        </div>
      </div>

      <div style={S.footer}>
        <Stars val={negocio.puntuacion} />
        <button style={S.reservarBtn} onClick={handleReservar}>
          Reservar <ChevronRight size={14} />
        </button>
      </div>
    </motion.div>
  )
}
