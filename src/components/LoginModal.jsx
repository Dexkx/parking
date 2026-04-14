import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Eye, EyeOff, Loader2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { authApi } from '../api/axios'
import { toast } from 'react-toastify'

const S = {
  overlay: {
    position: 'fixed', inset: 0, zIndex: 1000,
    background: 'rgba(0,0,0,0.75)',
    backdropFilter: 'blur(8px)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    padding: '1rem',
  },
  modal: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-xl)',
    width: '100%', maxWidth: 420,
    overflow: 'hidden',
    boxShadow: '0 24px 80px rgba(0,0,0,0.6)',
  },
  header: {
    padding: '1.5rem 1.5rem 0',
    display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
  },
  title: {
    fontFamily: 'var(--font-head)', fontWeight: 800, fontSize: 24,
    color: 'var(--text-primary)', letterSpacing: '-0.5px',
  },
  subtitle: { fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 },
  closeBtn: {
    background: 'var(--bg-input)', border: '1px solid var(--border)',
    borderRadius: 8, padding: 6, cursor: 'pointer',
    color: 'var(--text-secondary)', display: 'flex',
  },
  tabs: {
    display: 'flex', gap: 4, margin: '1.25rem 1.5rem 0',
    background: 'var(--bg-input)', borderRadius: 'var(--radius-sm)',
    padding: 4,
  },
  tab: (active) => ({
    flex: 1, padding: '8px 0', border: 'none', cursor: 'pointer',
    borderRadius: 6, fontSize: 13, fontWeight: 600,
    background: active ? 'var(--bg-card)' : 'transparent',
    color: active ? 'var(--text-primary)' : 'var(--text-muted)',
    boxShadow: active ? '0 1px 6px rgba(0,0,0,0.3)' : 'none',
    transition: 'all .2s',
  }),
  body: { padding: '1.25rem 1.5rem 1.5rem' },
  group: { display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 14 },
  label: { fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)', letterSpacing: '0.04em' },
  inputWrap: { position: 'relative' },
  input: {
    width: '100%', padding: '10px 14px',
    background: 'var(--bg-input)', border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)', color: 'var(--text-primary)',
    fontSize: 14, outline: 'none', transition: 'border .2s',
    fontFamily: 'var(--font-body)',
  },
  eyeBtn: {
    position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)',
    background: 'none', border: 'none', cursor: 'pointer',
    color: 'var(--text-muted)', padding: 0, display: 'flex',
  },
  submitBtn: {
    width: '100%', padding: '11px',
    background: 'var(--accent)', border: 'none',
    borderRadius: 'var(--radius-sm)', color: '#000',
    fontFamily: 'var(--font-head)', fontWeight: 700, fontSize: 15,
    cursor: 'pointer', display: 'flex', alignItems: 'center',
    justifyContent: 'center', gap: 8, marginTop: 8,
    transition: 'opacity .2s',
  },
  divider: {
    display: 'flex', alignItems: 'center', gap: 10,
    color: 'var(--text-muted)', fontSize: 12, margin: '14px 0',
  },
  line: { flex: 1, height: 1, background: 'var(--border)' },
}

export default function LoginModal({ open, onClose }) {
  const { login } = useAuth()
  const [tab, setTab] = useState('login') // 'login' | 'register'
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    numero_id: '', password: '', nombre: '',
    tipo_id: 'CC', confirm_password: '',
  })

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(form.numero_id, form.password)
      toast.success('¡Bienvenido de nuevo!')
      onClose()
    } catch {
      toast.error('Credenciales incorrectas')
    } finally { setLoading(false) }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    if (form.password !== form.confirm_password) {
      toast.warning('Las contraseñas no coinciden')
      return
    }
    setLoading(true)
    try {
      await authApi.register(form)
      toast.success('Cuenta creada. Ya puedes ingresar.')
      setTab('login')
    } catch (err) {
      const msg = err.response?.data ? JSON.stringify(err.response.data) : 'Error al registrarse'
      toast.error(msg)
    } finally { setLoading(false) }
  }

  if (!open) return null

  return (
    <AnimatePresence>
      <motion.div
        style={S.overlay}
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
        onClick={(e) => e.target === e.currentTarget && onClose()}
      >
        <motion.div
          style={S.modal}
          initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: 20 }}
          transition={{ type: 'spring', stiffness: 280, damping: 24 }}
        >
          <div style={S.header}>
            <div>
              <div style={S.title}>{tab === 'login' ? 'Bienvenido' : 'Crear cuenta'}</div>
              <div style={S.subtitle}>
                {tab === 'login' ? 'Ingresa para reservar tu espacio' : 'Regístrate y empieza a reservar'}
              </div>
            </div>
            <button style={S.closeBtn} onClick={onClose}><X size={16} /></button>
          </div>

          {/* Tabs */}
          <div style={S.tabs}>
            <button style={S.tab(tab === 'login')} onClick={() => setTab('login')}>Ingresar</button>
            <button style={S.tab(tab === 'register')} onClick={() => setTab('register')}>Registrarse</button>
          </div>

          <div style={S.body}>
            {tab === 'login' ? (
              <form onSubmit={handleLogin}>
                <div style={S.group}>
                  <label style={S.label}>N° IDENTIFICACIÓN</label>
                  <input style={S.input} value={form.numero_id} onChange={set('numero_id')}
                    placeholder="Ej: 1234567890" required />
                </div>
                <div style={S.group}>
                  <label style={S.label}>CONTRASEÑA</label>
                  <div style={S.inputWrap}>
                    <input style={{ ...S.input, paddingRight: 40 }}
                      type={showPass ? 'text' : 'password'}
                      value={form.password} onChange={set('password')} required />
                    <button type="button" style={S.eyeBtn} onClick={() => setShowPass(p => !p)}>
                      {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>
                <button style={S.submitBtn} disabled={loading}>
                  {loading ? <Loader2 size={16} className="spin" /> : 'Ingresar'}
                </button>
              </form>
            ) : (
              <form onSubmit={handleRegister}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 12px' }}>
                  <div style={S.group}>
                    <label style={S.label}>TIPO ID</label>
                    <select style={S.input} value={form.tipo_id} onChange={set('tipo_id')}>
                      <option value="CC">Cédula (CC)</option>
                      <option value="TI">T. Identidad (TI)</option>
                      <option value="CE">C. Extranjería (CE)</option>
                      <option value="PPT">PPT</option>
                    </select>
                  </div>
                  <div style={S.group}>
                    <label style={S.label}>N° IDENTIFICACIÓN</label>
                    <input style={S.input} value={form.numero_id} onChange={set('numero_id')}
                      placeholder="1234567890" required />
                  </div>
                </div>
                <div style={S.group}>
                  <label style={S.label}>NOMBRE COMPLETO</label>
                  <input style={S.input} value={form.nombre} onChange={set('nombre')}
                    placeholder="Tu nombre" required />
                </div>
                <div style={S.group}>
                  <label style={S.label}>CONTRASEÑA</label>
                  <div style={S.inputWrap}>
                    <input style={{ ...S.input, paddingRight: 40 }}
                      type={showPass ? 'text' : 'password'}
                      value={form.password} onChange={set('password')} required />
                    <button type="button" style={S.eyeBtn} onClick={() => setShowPass(p => !p)}>
                      {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>
                <div style={S.group}>
                  <label style={S.label}>CONFIRMAR CONTRASEÑA</label>
                  <input style={S.input} type="password" value={form.confirm_password}
                    onChange={set('confirm_password')} required />
                </div>
                <button style={S.submitBtn} disabled={loading}>
                  {loading ? <Loader2 size={16} /> : 'Crear cuenta'}
                </button>
              </form>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
