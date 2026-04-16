# ParkApp — Frontend Vue 3

Interfaz de usuario para la plataforma de parqueaderos ParkApp.

## Stack

| Herramienta | Propósito |
|---|---|
| **Vue 3** (Composition API) | Framework principal |
| **Pinia** | Estado global (auth, negocios) |
| **Vue Router 4** | Navegación con guards |
| **Tailwind CSS 3** | Estilos utilitarios + tema dark |
| **Axios** | Cliente HTTP con interceptores JWT |
| **SweetAlert2** | Modales de confirmación y tickets |
| **Vue Toastification** | Notificaciones toast |
| **@vue-leaflet/vue-leaflet** | Mapa interactivo |
| **Lucide Vue Next** | Íconos |
| **date-fns** | Formateo de fechas |
| **@vueuse/core** | Composables utilitarios |

---

## Arranque rápido

```bash
# 1. Instalar dependencias
npm install

# 2. Correr en desarrollo
npm run dev
```

El proxy en `vite.config.js` redirige `/api/*` → `http://localhost:8000`
así que Django debe estar corriendo antes de iniciar el frontend.

---

## Estructura del proyecto

```
src/
├── api/
│   └── axios.js          ← Cliente Axios + todos los endpoints del backend
│
├── stores/
│   ├── auth.js           ← Pinia: login, logout, sesión persistida
│   └── negocios.js       ← Pinia: lista y detalle de parqueaderos
│
├── router/
│   └── index.js          ← Rutas + guard de autenticación
│
├── composables/
│   └── useSwal.js        ← SweetAlert2 con tema dark (confirmación, ticket, reserva)
│
├── components/
│   ├── AppNavbar.vue     ← Barra de navegación sticky con blur
│   ├── LoginModal.vue    ← Modal login/registro con tabs
│   ├── ParkCard.vue      ← Tarjeta de parqueadero con reserva integrada
│   └── MapView.vue       ← Mapa Leaflet con marcadores custom
│
├── pages/
│   ├── HomePage.vue      ← Hero split (copy + mapa) + features
│   ├── ResultadosPage.vue← Sidebar lista + mapa + filtros
│   └── MisReservasPage.vue ← Reservas del usuario con ticket y cancelación
│
├── assets/
│   └── main.css          ← Tailwind + variables CSS + overrides globales
│
├── App.vue               ← Raíz: layout, LoginModal global, transición de rutas
└── main.js               ← Registro de plugins (Pinia, Router, Toast)
```

---

## Conexión con el backend Django

Todos los endpoints están centralizados en `src/api/axios.js`:

```
POST  /api/token                      → Login (obtener JWT)
POST  /api/token/refresh              → Renovar token
POST  /api/usuarios                   → Registro
GET   /api/usuarios/:id               → Perfil

GET   /api/negocios                   → Lista parqueaderos (mapa + resultados)
GET   /api/negocios/:nit              → Detalle parqueadero
GET   /api/negocios/:nit/resenas      → Reseñas
POST  /api/negocios/:nit/resenas      → Crear reseña
GET   /api/negocios/:nit/tarifas      → Tarifas
GET   /api/negocios/:nit/reservas     → Reservas del usuario
POST  /api/negocios/:nit/reservas     → Crear reserva
DELETE /api/negocios/:nit/reservas/:uuid → Cancelar
```

El interceptor de Axios inyecta automáticamente el `Bearer token` en
cada request y hace refresh silencioso si el access token expira.

---

## Variables de entorno

Crea un archivo `.env.local` si necesitas cambiar la URL del backend:

```env
VITE_API_URL=http://localhost:8000
```

Y actualiza `vite.config.js` → `server.proxy.target` con ese valor.
