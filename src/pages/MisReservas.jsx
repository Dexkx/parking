import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { CalendarClock, MapPin, Car, Clock, XCircle, Receipt, Star } from 'lucide-react'
import { format, formatDistanceToNow, isPast } from 'date-fns'
import { es } from 'date-fns/locale'
import Swal from 'sweetalert2'
import { toast } from 'react-toastify'
import { useAuth } from '../context/AuthContext'
import { reservasApi, negociosApi } from '../api/axios'

const S = {
  page: { maxWidth: 900, margin: '0 auto', padding: '2.5rem 1.5rem' },
  header: { marginBottom: '2rem' },
  title: {
    fontFamily: 'var(--font-head)', fontWeight: 800, fontSize: 32,
    color: 'var(--text-primary)', letterSpacing: '-1px', marginBottom: 6,
  },
  sub: { color: 'var(--text-secondary)', fontSize: 15 },
  tabs: {
    display: 'flex', gap: 4, marginBottom: '1.5rem',
    background: 'var(--bg-card)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius-md)', padding: 4, width: 'fit-content',
  },
  tab: (a) => ({
    padding: '7px 20px', borderRadius: 8, border: 'none',
    fontFamily: 'var(--font-head)', fontWeight: 600, fontSize: 13,
    cursor: 'pointer', transition: 'all .2s',
    background: a ? 'var(--bg-surface)' : 'transparent',
    color: a ? 'var(--accent)' : 'var(--text-secondary)',
    boxShadow: a ? '0 1px 6px rgba(0,0,0,0.3)' : 'none',
  }),
  card: {
    background: 'var(--bg-card)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)', overflow: 'hidden',
    marginBottom: 12,
  },
  cardHead: {
    padding: '1rem 1.25rem',
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    borderBottom: '1px solid var(--border)',
  },
  negNombre: {
    fontFamily: 'var(--font-head)', fontWeight: 700, fontSize: 16,
    color: 'var(--text-primary)',
  },
  cardBody: {
    padding: '1rem 1.25rem',
    display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16,
  },
  infoItem: { display: 'flex', flexDirection: 'column', gap: 3 },
  infoLabel: { fontSize: 11, color: 'var(--text-muted)', fontWeight: 500, letterSpacing: '0.06em' },
  infoVal: { fontSize: 14, color: 'var(--text-primary)', fontWeight: 500 },
  cardFoot: {
    padding: '0.75rem 1.25rem',
    display: 'flex', justifyContent: 'flex-end', alignItems: 'center',
    gap: 8, background: 'var(--bg-input)',
  },
  cancelBtn: {
    display: 'flex', alignItems: 'center', gap: 5,
    padding: '6px 14px', borderRadius: 'var(--radius-sm)',
    background: 'rgba(255,77,109,0.1)', border: '1px solid rgba(255,77,109,0.25)',
    color: 'var(--danger)', fontSize: 13, cursor: 'pointer',
    fontFamily: 'var(--font-body)',
  },
  ticketBtn: {
    display: 'flex', alignItems: 'center', gap: 5,
    padding: '6px 14px', borderRadius: 'var(--radius-sm)',
    background: 'var(--accent-dim)', border: '1px solid rgba(0,229,176,0.25)',
    color: 'var(--accent)', fontSize: 13, cursor: 'pointer',
    fontFamily: 'var(--font-body)',
  },
  empty: {
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    padding: '4rem', gap: 12, color: 'var(--text-muted)',
  },
  badge: (color) => ({
    display: 'inline-flex', alignItems: 'center', gap: 4,
    padding: '3px 10px', borderRadius: 100, fontSize: 11, fontWeight: 600,
    background: color === 'green' ? 'rgba(0,229,176,0.12)'
      : color === 'red' ? 'rgba(255,77,109,0.12)'
      : 'rgba(79,142,247,0.12)',
    color: color === 'green' ? 'var(--accent)'
      : color === 'red' ? 'var(--danger)'
      : 'var(--blue)',
    border: `1px solid ${color === 'green' ? 'rgba(0,229,176,0.3)'
      : color === 'red' ? 'rgba(255,77,109,0.3)'
      : 'rgba(79,142,247,0.3)'}`,
  }),
}

function StatusBadge({ reserva }) {
  const pasado = isPast(new Date(reserva.hf_final))
  const estado = reserva.status === 'Cancelado' ? 'red'
    : pasado ? 'blue' : 'green'
  const label = reserva.status === 'Cancelado' ? 'Cancelada'
    : pasado ? 'Completada' : 'Activa'
  return <span style={S.badge(estado)}>{label}</span>
}

function ReservaCard({ reserva, onCancel }) {
  const pasado = isPast(new Date(reserva.hf_final))

  const mostrarTicket = async () => {
    await Swal.fire({
      title: `<span style="font-family:Syne;font-weight:800;color:#eef0f5">Ticket de Reserva</span>`,
      html: `
        <div style="font-family:DM Sans;text-align:left;background:#161922;padding:16px;border-radius:12px;border:1px solid rgba(255,255,255,0.07)">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div><div style="font-size:10px;color:#4e5568;letter-spacing:.06em;margin-bottom:3px">PARQUEADERO</div><div style="color:#eef0f5;font-weight:600">${reserva.negocio}</div></div>
            <div><div style="font-size:10px;color:#4e5568;letter-spacing:.06em;margin-bottom:3px">PLACA</div><div style="color:#00e5b0;font-weight:700;font-size:18px;font-family:Syne">${reserva.placa}</div></div>
            <div><div style="font-size:10px;color:#4e5568;letter-spacing:.06em;margin-bottom:3px">PISO</div><div style="color:#eef0f5">${reserva.piso || '—'}</div></div>
            <div><div style="font-size:10px;color:#4e5568;letter-spacing:.06em;margin-bottom:3px">PUESTO</div><div style="color:#eef0f5;font-weight:600">#${reserva.numero || '—'}</div></div>
            <div><div style="font-size:10px;color:#4e5568;letter-spacing:.06em;margin-bottom:3px">ENTRADA</div><div style="color:#eef0f5">${format(new Date(reserva.hf_inicio), 'dd/MM/yyyy HH:mm')}</div></div>
            <div><div style="font-size:10px;color:#4e5568;letter-spacing:.06em;margin-bottom:3px">SALIDA</div><div style="color:#eef0f5">${format(new Date(reserva.hf_final), 'dd/MM/yyyy HH:mm')}</div></div>
          </div>
          <div style="margin-top:14px;padding-top:14px;border-top:1px solid rgba(255,255,255,0.07);display:flex;justify-content:space-between;align-items:center">
            <div style="font-size:10px;color:#4e5568">TOTAL PAGADO</div>
            <div style="font-family:Syne;font-weight:800;font-size:22px;color:#00e5b0">$${Number(reserva.valor_pagado || 0).toLocaleString('es-CO')}</div>
          </div>
        </div>
      `,
      background: '#0f1117',
      showConfirmButton: true,
      confirmButtonText: 'Cerrar',
      confirmButtonColor: '#374151',
    })
  }

  return (
    <motion.div style={S.card}
      initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -20 }} layout
    >
      <div style={S.cardHead}>
        <div>
          <div style={S.negNombre}>{reserva.negocio || 'Parqueadero'}</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2, display: 'flex', alignItems: 'center', gap: 4 }}>
            <Clock size={11} />
            {!pasado
              ? `Termina ${formatDistanceToNow(new Date(reserva.hf_final), { addSuffix: true, locale: es })}`
              : `Completada ${formatDistanceToNow(new Date(reserva.hf_final), { addSuffix: true, locale: es })}`}
          </div>
        </div>
        <StatusBadge reserva={reserva} />
      </div>

      <div style={S.cardBody}>
        <div style={S.infoItem}>
          <span style={S.infoLabel}>PLACA</span>
          <span style={{ ...S.infoVal, color: 'var(--accent)', fontFamily: 'var(--font-head)', fontWeight: 700 }}>
            {reserva.placa}
          </span>
        </div>
        <div style={S.infoItem}>
          <span style={S.infoLabel}>PISO / PUESTO</span>
          <span style={S.infoVal}>{reserva.piso || '—'} / #{reserva.numero || '—'}</span>
        </div>
        <div style={S.infoItem}>
          <span style={S.infoLabel}>ENTRADA</span>
          <span style={S.infoVal}>{format(new Date(reserva.hf_inicio), 'dd MMM, HH:mm', { locale: es })}</span>
        </div>
        <div style={S.infoItem}>
          <span style={S.infoLabel}>TOTAL</span>
          <span style={{ ...S.infoVal, fontFamily: 'var(--font-head)', fontWeight: 700 }}>
            ${Number(reserva.valor_pagado || 0).toLocaleString('es-CO')}
          </span>
        </div>
      </div>

      <div style={S.cardFoot}>
        <button style={S.ticketBtn} onClick={mostrarTicket}>
          <Receipt size={13} /> Ver ticket
        </button>
        {!pasado && reserva.status !== 'Cancelado' && (
          <button style={S.cancelBtn} onClick={() => onCancel(reserva)}>
            <XCircle size={13} /> Cancelar
          </button>
        )}
      </div>
    </motion.div>
  )
}

export default function MisReservas() {
  const { user, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [reservas, setReservas] = useState([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('activas')

  useEffect(() => {
    if (!isAuthenticated) { navigate('/'); return }
    // Cargar reservas de todos los negocios (en producción filtrarías por usuario)
    negociosApi.list().then(async (res) => {
      const negs = res.data?.results ?? res.data ?? []
      const promises = negs.map(n =>
        reservasApi.mis(n.nit).then(r => (r.data?.results ?? r.data ?? []).map(rv => ({ ...rv, negocio: n.nombre }))).catch(() => [])
      )
      const all = (await Promise.all(promises)).flat()
      setReservas(all)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [isAuthenticated])

  const handleCancel = async (reserva) => {
    const { isConfirmed } = await Swal.fire({
      title: '<span style="font-family:Syne;color:#eef0f5">¿Cancelar reserva?</span>',
      html: '<span style="color:#8b92a8">Esta acción no se puede deshacer.</span>',
      icon: 'warning',
      background: '#161922',
      showCancelButton: true,
      confirmButtonText: 'Sí, cancelar',
      cancelButtonText: 'Volver',
      confirmButtonColor: '#ff4d6d',
      cancelButtonColor: '#374151',
    })
    if (!isConfirmed) return
    try {
      await reservasApi.cancelar(reserva.negocio_id, reserva.uuid)
      setReservas(r => r.map(rv => rv.uuid === reserva.uuid ? { ...rv, status: 'Cancelado' } : rv))
      toast.success('Reserva cancelada')
    } catch { toast.error('No se pudo cancelar') }
  }

  const activas = reservas.filter(r => !isPast(new Date(r.hf_final)) && r.status !== 'Cancelado')
  const pasadas = reservas.filter(r => isPast(new Date(r.hf_final)) || r.status === 'Cancelado')
  const lista = tab === 'activas' ? activas : pasadas

  return (
    <div style={S.page}>
      <div style={S.header}>
        <h1 style={S.title}>Mis Reservas</h1>
        <p style={S.sub}>Hola, <strong style={{ color: 'var(--accent)' }}>{user?.nombre?.split(' ')[0] || 'usuario'}</strong>. Aquí están tus reservas.</p>
      </div>

      <div style={S.tabs}>
        <button style={S.tab(tab === 'activas')} onClick={() => setTab('activas')}>
          Activas ({activas.length})
        </button>
        <button style={S.tab(tab === 'historial')} onClick={() => setTab('historial')}>
          Historial ({pasadas.length})
        </button>
      </div>

      {loading ? (
        <div style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 8 }}>
          <CalendarClock size={16} /> Cargando reservas...
        </div>
      ) : lista.length === 0 ? (
        <div style={S.empty}>
          <CalendarClock size={48} strokeWidth={1} />
          <div style={{ fontFamily: 'var(--font-head)', fontWeight: 700, fontSize: 18 }}>
            {tab === 'activas' ? 'No tienes reservas activas' : 'Sin historial'}
          </div>
          <div style={{ fontSize: 14 }}>
            {tab === 'activas' && 'Busca un parqueadero y reserva tu espacio.'}
          </div>
        </div>
      ) : (
        <AnimatePresence mode="popLayout">
          {lista.map((r) => <ReservaCard key={r.uuid} reserva={r} onCancel={handleCancel} />)}
        </AnimatePresence>
      )}
    </div>
  )
}
