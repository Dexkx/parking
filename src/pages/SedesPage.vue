<script setup>
/**
 * SedesPage.vue
 * Ruta: /negocios/:nit/sedes
 *
 * Al crear o editar una sede, se geocodifica la dirección
 * automáticamente con Nominatim para obtener lat/lng sin
 * que el usuario tenga que escribirlos.
 */
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Plus, Pencil, Trash2, MapPin, ParkingCircle,
  ChevronRight, ArrowLeft, Loader2, Navigation
} from 'lucide-vue-next'
import CrudModal from '@/components/CrudModal.vue'
import { sedesApi, negociosApi, catalogosApi } from '@/api/axios'
import { useGeocoder } from '@/composables/useGeocoder'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'

const route  = useRoute()
const router = useRouter()
const toast  = useToast()
const { geocodificar, geocoding, error: geocodingError } = useGeocoder()
const auth   = useAuthStore()

const nit     = route.params.nit
const negocio = ref(null)
const items   = ref([])
const paises  = ref([])
const deptos  = ref([])
const ciudades = ref([])
const loading  = ref(true)
const saving   = ref(false)
const modal    = ref({ open: false, mode: 'create', item: null })

// lat/lng resueltos por geocoding (solo se muestran como preview)
const coordsPreview = ref(null)

const emptyForm = () => ({
  negocio: nit, nombre: '', direccion: '',
  country: '', state: '', city: '',
  creado_por: auth.user?.numero_id ?? '',
})
const form = ref(emptyForm())

onMounted(async () => {
  const [negRes, sedesRes, paisRes] = await Promise.all([
    negociosApi.list(),
    sedesApi.list(nit),
    catalogosApi.paises(),
  ])
  const negs    = negRes.data?.results  ?? negRes.data  ?? []
  negocio.value = negs.find(n => n.nit === nit) ?? null
  items.value   = sedesRes.data?.results ?? sedesRes.data ?? []
  paises.value  = paisRes.data?.results  ?? paisRes.data  ?? []
  loading.value = false
})

// ── Cascada país → depto → ciudad ─────────
async function onPaisChange() {
  form.value.state = ''
  form.value.city = ''
  ciudades.value = []
  coordsPreview.value = null
  if (!form.value.country) { deptos.value = []; return }
  await getDeptos()
}
async function getDeptos(){
  const res = await catalogosApi.departamentos(form.value.country)
  deptos.value = res.data?.results ?? res.data ?? []
}
async function onDeptoChange() {
  form.value.city = ''
  coordsPreview.value = null
  if (!form.value.state) { ciudades.value = []; return }
  await getCiudades()
}
async function getCiudades(){
  const res = await catalogosApi.ciudades(form.value.country, form.value.state)
  ciudades.value = res.data?.results ?? res.data ?? []
}

// ── Geocodificación ────────────────────────
/**
 * Se llama cuando el usuario sale del campo de dirección (blur).
 * Si hay dirección escrita, busca las coordenadas y las muestra
 * como preview en verde para que el usuario sepa que funcionó.
 */
async function handleDireccionBlur() {
  coordsPreview.value = null
  if (!form.value.direccion?.trim()) return

  // Construir contexto de ciudad para mejorar la búsqueda
  const ciudadNombre = ciudades.value.find(c => c.id === form.value.city)?.name ?? ''
  const paisNombre   = paises.value.find(p => p.id === form.value.country)?.name ?? 'Colombia'
  const contexto     = [ciudadNombre, paisNombre].filter(Boolean).join(', ')

  const coords = await geocodificar(form.value.direccion, contexto)
  if (coords) {
    coordsPreview.value = coords
  } else if (geocodingError.value) {
    // No bloquear al usuario, solo avisarle
    toast.warning(`Geocodificación: ${geocodingError.value}. La sede se guardará sin coordenadas.`)
  }
}

// ── Modales ────────────────────────────────
function openCreate() {
  form.value = emptyForm()
  coordsPreview.value = null
  modal.value = { open: true, mode: 'create', item: null }
}
async function openEdit(item) {
  form.value = {
    negocio:      nit,
    nombre:       item.nombre,
    direccion:    item.direccion,
    country:      item.country?.id ?? '',
    state:        item.state?.id ?? '',
    city:         item.city?.id ?? '',
  }
  // Mostrar coords actuales si existen
  coordsPreview.value = (item.lat && item.lng)
    ? { lat: Number(item.lat), lng: Number(item.lng) }
    : null
  modal.value = { open: true, mode: 'edit', item }

  // Obtener dptos y ciudades
  await getDeptos()
  await getCiudades()
}
function closeModal() {
  modal.value.open = false
  coordsPreview.value = null
}

// ── Guardar ────────────────────────────────
async function handleSubmit() {
  saving.value = true
  try {
    // Si no tenemos coords todavía, intentar una última vez
    if (!coordsPreview.value && form.value.direccion?.trim()) {
      const ciudadNombre = ciudades.value.find(c => c.id === form.value.city)?.name ?? ''
      const paisNombre   = paises.value.find(p => p.id === form.value.country)?.name ?? 'Colombia'
      coordsPreview.value = await geocodificar(form.value.direccion, [ciudadNombre, paisNombre].join(', '))
    }

    // Construir payload: incluir lat/lng si los tenemos
    const payload = {
      ...form.value,
      ...(coordsPreview.value
        ? { lat: coordsPreview.value.lat, lng: coordsPreview.value.lng }
        : {}),
    }

    if (modal.value.mode === 'create') {
      await sedesApi.create(nit, payload)
      toast.success('Sede creada con éxito' + (coordsPreview.value ? ' · Aparecerá en el mapa.' : ' · Sin coordenadas GPS.'))
    } else {
      await sedesApi.update(nit, modal.value.item.uuid, payload)
      toast.success('Sede actualizada')
    }

    closeModal()
    const res = await sedesApi.list(nit)
    items.value = res.data?.results ?? res.data ?? []
  } catch (err) {
    const msg = err.response?.data
      ? Object.values(err.response.data).flat().join(' · ')
      : 'Error al guardar'
    toast.error(msg)
  } finally { saving.value = false }
}

// ── Eliminar ───────────────────────────────
async function handleDelete(item) {
  if (!confirm(`¿Eliminar la sede "${item.nombre}"?`)) return
  try {
    await sedesApi.remove(nit, item.uuid)
    toast.success('Sede eliminada')
    items.value = items.value.filter(s => s.uuid !== item.uuid)
  } catch { toast.error('No se pudo eliminar') }
}

const irPuestos = (sedeUuid) => router.push({ name: 'puestos', params: { nit, sede: sedeUuid } })
</script>

<template>
  <div class="p-6 max-w-screen-lg mx-auto">

    <!-- Back -->
    <button class="flex items-center gap-1.5 text-xs text-t-muted hover:text-t-primary transition-colors mb-5"
            @click="router.back()">
      <ArrowLeft :size="13" /> Volver a negocios
    </button>

    <!-- Header -->
    <div class="flex justify-between items-start mb-7">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <ParkingCircle :size="16" class="text-accent" />
          <span class="text-xs text-t-muted font-medium">{{ negocio?.nombre ?? nit }}</span>
        </div>
        <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Sedes</h1>
        <p class="text-t-secondary text-sm mt-1">
          Cada sede es una ubicación física. Las coordenadas se detectan automáticamente de la dirección.
        </p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus :size="15" /> Nueva sede
      </button>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="flex flex-col gap-3">
      <div v-for="i in 3" :key="i" class="skeleton h-24" />
    </div>

    <!-- Vacío -->
    <div v-else-if="items.length === 0" class="card-dark rounded-lg py-16 text-center">
      <MapPin :size="40" class="text-t-muted mx-auto mb-3" :stroke-width="1" />
      <p class="font-head font-bold text-t-primary mb-1">Sin sedes registradas</p>
      <p class="text-sm text-t-secondary">Agrega la primera sede para poder crear puestos y tarifas.</p>
    </div>

    <!-- Lista -->
    <div v-else class="flex flex-col gap-3">
      <div v-for="s in items" :key="s.uuid"
           class="card-dark rounded-lg overflow-hidden hover:border-border-hover transition-all animate-fade-up">
        <div class="flex items-center gap-4 p-4">

          <!-- Icono -->
          <div class="w-10 h-10 rounded-sm bg-blue/10 border border-blue/20 flex items-center justify-center shrink-0">
            <MapPin :size="18" class="text-blue" />
          </div>

          <!-- Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-0.5">
              <span class="font-head font-bold text-t-primary text-sm">{{ s.nombre }}</span>
              <span :class="s.status === 'Activo' ? 'badge-green' : 'badge-red'">{{ s.status }}</span>
              <!-- Indicador de coordenadas GPS -->
              <span v-if="s.lat && s.lng"
                    class="inline-flex items-center gap-1 text-[10px] font-medium text-accent/70">
                <Navigation :size="9" /> GPS
              </span>
            </div>
            <div class="flex items-center gap-1 text-xs text-t-secondary">
              <MapPin :size="10" class="text-t-muted shrink-0" />
              <span class="truncate">{{ s.direccion }}</span>
              <span v-if="s.ciudad?.name" class="text-t-muted shrink-0">— {{ s.ciudad.name }}</span>
            </div>
          </div>

          <!-- Stats -->
          <div class="hidden md:flex items-center gap-5 text-center shrink-0">
            <div>
              <div class="text-[10px] text-t-muted uppercase tracking-wider">Puestos</div>
              <div class="font-head font-bold text-accent text-sm">{{ s.puestos_count ?? 0 }}</div>
            </div>
            <div>
              <div class="text-[10px] text-t-muted uppercase tracking-wider">Puntuación</div>
              <div class="font-head font-bold text-warn text-sm">
                {{ s.puntuacion ? Number(s.puntuacion).toFixed(1) : '—' }} ★
              </div>
            </div>
          </div>

          <!-- Acciones -->
          <div class="flex items-center gap-1.5 shrink-0">
            <button class="btn-icon w-8 h-8" title="Editar" @click="openEdit(s)"><Pencil :size="13" /></button>
            <button class="btn-icon w-8 h-8 hover:text-danger hover:border-danger/30"
                    title="Eliminar" @click="handleDelete(s)"><Trash2 :size="13" /></button>
            <button class="btn-primary text-xs px-3 py-1.5 ml-1" @click="irPuestos(s.uuid)">
              Puestos <ChevronRight :size="12" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal crear/editar sede -->
    <CrudModal :open="modal.open"
               :title="modal.mode === 'create' ? 'Nueva sede' : 'Editar sede'"
               :loading="saving || geocoding"
               :submit-label="saving ? 'Guardando...' : geocoding ? 'Buscando coordenadas...' : 'Guardar sede'"
               size="lg" @close="closeModal" @submit="handleSubmit">

      <!-- Nombre -->
      <div>
        <label class="label-dark">NOMBRE DE LA SEDE</label>
        <input class="input-dark" v-model="form.nombre"
               placeholder="Ej: Sede Norte, Sede Chapinero" required />
      </div>

      <!-- Dirección con geocoding al perder el foco -->
      <div>
        <label class="label-dark">DIRECCIÓN</label>
        <div class="relative">
          <input class="input-dark pr-10" v-model="form.direccion"
                 placeholder="Calle 26 # 13-20"
                 required
                 @blur="handleDireccionBlur" />
          <!-- Spinner de geocoding -->
          <div v-if="geocoding"
               class="absolute right-3 top-1/2 -translate-y-1/2 text-t-muted">
            <Loader2 :size="14" class="animate-spin" />
          </div>
          <!-- Check si encontró coords -->
          <div v-else-if="coordsPreview"
               class="absolute right-3 top-1/2 -translate-y-1/2 text-accent">
            <Navigation :size="14" />
          </div>
        </div>

        <!-- Preview de coordenadas encontradas -->
        <div v-if="coordsPreview"
             class="mt-1.5 flex items-center gap-1.5 text-xs text-accent">
          <Navigation :size="10" />
          <span class="font-mono">
            {{ coordsPreview.lat.toFixed(5) }}, {{ coordsPreview.lng.toFixed(5) }}
          </span>
          <span class="text-t-muted">— Aparecerá en el mapa automáticamente</span>
        </div>
        <p v-else-if="!geocoding && form.direccion"
           class="mt-1 text-xs text-t-muted">
          Las coordenadas GPS se detectan al escribir la dirección. Si no las encuentra puedes continuar igual.
        </p>
      </div>

      <!-- País / Departamento / Ciudad -->
      <div class="grid grid-cols-3 gap-3">
        <div>
          <label class="label-dark">PAÍS</label>
          <select class="input-dark" v-model="form.country" @change="onPaisChange" required>
            <option value="">Selecciona</option>
            <option v-for="p in paises" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>
        <div>
          <label class="label-dark">DEPARTAMENTO</label>
          <select class="input-dark" v-model="form.state"
                  @change="onDeptoChange" required
                  :disabled="!deptos.length">
            <option value="">Selecciona</option>
            <option v-for="d in deptos" :key="d.id" :value="d.id">{{ d.name }}</option>
          </select>
        </div>
        <div>
          <label class="label-dark">CIUDAD</label>
          <select class="input-dark" v-model="form.city" :disabled="!ciudades.length">
            <option value="">Selecciona</option>
            <option v-for="c in ciudades" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
      </div>

    </CrudModal>

  </div>
</template>
