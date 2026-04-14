import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import { motion } from 'framer-motion'
import { MapPin, Star } from 'lucide-react'

// Icono custom verde
const createIcon = (disponible) => L.divIcon({
  className: '',
  html: `<div style="
    width:36px;height:36px;
    background:${disponible ? '#00e5b0' : '#4e5568'};
    border:2.5px solid ${disponible ? '#fff' : '#2a2d38'};
    border-radius:50% 50% 50% 0;
    transform:rotate(-45deg);
    box-shadow:0 4px 14px rgba(0,0,0,0.4);
    display:flex;align-items:center;justify-content:center;
  "><div style="transform:rotate(45deg);color:${disponible ? '#000' : '#aaa'};font-size:13px">P</div></div>`,
  iconSize: [36, 36],
  iconAnchor: [18, 36],
  popupAnchor: [0, -36],
})

function FlyToCenter({ center }) {
  const map = useMap()
  useEffect(() => { if (center) map.flyTo(center, 13, { duration: 1.2 }) }, [center])
  return null
}

export default function MapView({ negocios = [], center = [4.711, -74.0721] }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      style={{ height: '100%', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}
    >
      <MapContainer
        center={center}
        zoom={12}
        style={{ height: '100%', width: '100%' }}
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap'
        />
        <FlyToCenter center={center} />
        {negocios.map((neg) => (
          <Marker
            key={neg.nit}
            position={[
              neg.lat ?? (4.711 + Math.random() * 0.05 - 0.025),
              neg.lng ?? (-74.072 + Math.random() * 0.05 - 0.025),
            ]}
            icon={createIcon(neg.status === 'Activo')}
          >
            <Popup>
              <div style={{ fontFamily: 'DM Sans', minWidth: 180 }}>
                <div style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 14, marginBottom: 4 }}>
                  {neg.nombre}
                </div>
                <div style={{ fontSize: 12, color: '#8b92a8', marginBottom: 8 }}>{neg.direccion}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
                  <span style={{ color: '#00e5b0', fontWeight: 600 }}>
                    {neg.tarifas?.[0]?.valor
                      ? `$${Number(neg.tarifas[0].valor).toLocaleString('es-CO')}/h`
                      : 'Ver tarifas'}
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                    <Star size={11} fill="#fbbf24" color="#fbbf24" />
                    {neg.puntuacion ? Number(neg.puntuacion).toFixed(1) : '—'}
                  </span>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </motion.div>
  )
}
