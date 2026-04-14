import { useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import LoginModal from './components/LoginModal'
import Home from './pages/Home'
import Resultados from './pages/Resultados'
import MisReservas from './pages/MisReservas'

export default function App() {
  const [loginOpen, setLoginOpen] = useState(false)

  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar onLoginOpen={() => setLoginOpen(true)} />
        <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />

        <Routes>
          <Route path="/" element={<Home onLoginOpen={() => setLoginOpen(true)} />} />
          <Route path="/resultados" element={<Resultados onLoginRequired={() => setLoginOpen(true)} />} />
          <Route path="/reservas" element={<MisReservas />} />
        </Routes>

        <ToastContainer
          position="bottom-right"
          autoClose={3500}
          hideProgressBar={false}
          newestOnTop
          closeOnClick
          pauseOnFocusLoss={false}
          draggable
          pauseOnHover
          theme="dark"
        />
      </BrowserRouter>
    </AuthProvider>
  )
}
