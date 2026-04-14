import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { MapPin, BookOpen, LogOut, LogIn, User, Menu, X } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { toast } from 'react-toastify'

const styles = {
  nav: {
    position: 'sticky', top: 0, zIndex: 100,
    background: 'rgba(8, 10, 15, 0.85)',
    backdropFilter: 'blur(20px)',
    borderBottom: '1px solid var(--border)',
    padding: '0 1.5rem',
  },
  inner: {
    maxWidth: 1280, margin: '0 auto',
    display: 'flex', alignItems: 'center',
    justifyContent: 'space-between',
    height: 64,
  },
  logo: {
    display: 'flex', alignItems: 'center', gap: 8,
    fontFamily: 'var(--font-head)',
    fontWeight: 800, fontSize: 22,
    letterSpacing: '-0.5px',
    color: 'var(--text-primary)',
  },
  logoP: { color: 'var(--accent)' },
  links: { display: 'flex', alignItems: 'center', gap: 4 },
  navLink: (active) => ({
    display: 'flex', alignItems: 'center', gap: 6,
    padding: '6px 14px', borderRadius: 'var(--radius-sm)',
    fontSize: 14, fontWeight: 500,
    color: active ? 'var(--accent)' : 'var(--text-secondary)',
    background: active ? 'var(--accent-dim)' : 'transparent',
    transition: 'all .2s',
    cursor: 'pointer', border: 'none',
    textDecoration: 'none',
  }),
  userChip: {
    display: 'flex', alignItems: 'center', gap: 8,
    padding: '5px 12px 5px 6px',
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 100,
    fontSize: 13, color: 'var(--text-secondary)',
    cursor: 'default',
  },
  avatar: {
    width: 28, height: 28, borderRadius: '50%',
    background: 'var(--accent-dim)',
    border: '1.5px solid var(--accent)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    color: 'var(--accent)', fontSize: 13,
  },
  logoutBtn: {
    display: 'flex', alignItems: 'center', gap: 6,
    padding: '6px 12px', borderRadius: 'var(--radius-sm)',
    background: 'transparent', border: '1px solid var(--border)',
    color: 'var(--text-secondary)', cursor: 'pointer',
    fontSize: 13, transition: 'all .2s',
  },
  loginBtn: {
    display: 'flex', alignItems: 'center', gap: 6,
    padding: '7px 16px', borderRadius: 'var(--radius-sm)',
    background: 'var(--accent)', border: 'none',
    color: '#000', cursor: 'pointer',
    fontSize: 14, fontWeight: 600,
    fontFamily: 'var(--font-head)',
    transition: 'all .2s',
  },
}

export default function Navbar({ onLoginOpen }) {
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    toast.info('Sesión cerrada')
    navigate('/')
  }

  const isActive = (path) => location.pathname === path

  return (
    <nav style={styles.nav}>
      <div style={styles.inner}>
        {/* Logo */}
        <Link to="/" style={styles.logo}>
          <MapPin size={20} color="var(--accent)" strokeWidth={2.5} />
          <span><span style={styles.logoP}>Park</span>App</span>
        </Link>

        {/* Links desktop */}
        <div style={styles.links}>
          <Link to="/" style={styles.navLink(isActive('/'))}>
            <MapPin size={15} /> Mapa
          </Link>
          <Link to="/resultados" style={styles.navLink(isActive('/resultados'))}>
            Parqueaderos
          </Link>
          {isAuthenticated && (
            <Link to="/reservas" style={styles.navLink(isActive('/reservas'))}>
              <BookOpen size={15} /> Mis Reservas
            </Link>
          )}
        </div>

        {/* Auth area */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {isAuthenticated ? (
            <>
              <div style={styles.userChip}>
                <div style={styles.avatar}>
                  <User size={13} />
                </div>
                <span>{user?.nombre?.split(' ')[0] || user?.numero_id}</span>
              </div>
              <button style={styles.logoutBtn} onClick={handleLogout}>
                <LogOut size={14} /> Salir
              </button>
            </>
          ) : (
            <button style={styles.loginBtn} onClick={onLoginOpen}>
              <LogIn size={15} /> Ingresar
            </button>
          )}
        </div>
      </div>
    </nav>
  )
}
