<script setup>
/**
 * SedesGeneralPage.vue
 * Ruta: /sedes?negocio=:nit
 *
 * Página general de sedes en el sidebar del dashboard.
 * Permite ver y gestionar las sedes de cualquier negocio
 * con un selector de negocio en la parte superior.
 *
 * Si llega con ?negocio=nit (desde NegociosPage),
 * pre-selecciona ese negocio automáticamente.
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Plus, Pencil, MapPin, ParkingCircle, Users, LandPlot,
  ChevronRight, Navigation, RefreshCcwDot, ThumbsUp, ThumbsDown
} from 'lucide-vue-next'
import CrudModal from '@/components/CrudModal.vue'
import { sedesApi, negociosApi, franquiciasApi, catalogosApi } from '@/api/axios'
import { useGeocoder } from '@/composables/useGeocoder'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { geocodificar } = useGeocoder()
const auth = useAuthStore()

// ── Estado ────────────────────────────────────────
const franquicias = ref([])
const negocios = ref([])  // todos los negocios
const negocioActivo = ref(route.query.negocio ?? '')  // nit del negocio seleccionado
const sedes = ref([])
const paises = ref([])
const deptos = ref([])
const ciudades = ref([])
const loading = ref(false)
const loadingNegocios = ref(true)
const saving = ref(false)
const modal = ref({ open: false, mode: 'create', item: null })
const askingLocates = ref(false)
const locates = ref([])
const selectedLocate = ref(null)

const emptyForm = () => ({
  negocio: negocioActivo.value, nombre: '', direccion: '',
  country: '', state: '', city: '',
  creado_por: auth.user?.numero_id ?? '',
  lat: null,
  lng: null,
  minutos_gracia: null,
})
const form = ref(emptyForm())
const hasCoords = computed(() => {
  return form.value.lat && form.value.lng
})

// ── Carga inicial ──────────────────────────────────
onMounted(async () => {
  const [sedRes, negRes, paisRes, franqRes] = await Promise.all([
    sedesApi.list(),
    negociosApi.list(),
    catalogosApi.paises(),
    franquiciasApi.list(),
  ])
  sedes.value = sedRes.data?.results ?? sedRes.data ?? []
  negocios.value = negRes.data?.results ?? negRes.data ?? []
  paises.value = paisRes.data?.results ?? paisRes.data ?? []
  franquicias.value = franqRes.data?.results ?? franqRes.data ?? []
  loadingNegocios.value = false
})

const sedesFiltradas = computed(() => {
  router.push(negocioActivo.value ? { query: { negocio: negocioActivo.value } } : {})

  if (!negocioActivo.value) return sedes.value

  return sedes.value.filter(s => s.negocio?.nit === negocioActivo.value)
})

// ── Cascada país → depto → ciudad ─────────────────
async function onPaisChange() {
  form.value.state = ''; form.value.city = ''
  ciudades.value = []

  await getDeptos()
}
async function getDeptos() {
  if (!form.value.country) { deptos.value = []; return }

  const res = await catalogosApi.departamentos(form.value.country)
  deptos.value = res.data?.results ?? res.data ?? []
}

async function onDeptoChange() {
  form.value.city = '';

  await getCities()
}
async function getCities() {
  if (!form.value.state) { ciudades.value = []; return }

  const res = await catalogosApi.ciudades(form.value.country, form.value.state)
  ciudades.value = res.data?.results ?? res.data ?? []
}

// ── Geocodificación ────────────────────────────────
async function handleDireccion() {
  askingLocates.value = true
  if (!form.value.direccion?.trim() || !form.value.state || !form.value.country) {
    askingLocates.value = false
    return
  }

  const cityNombre = ciudades.value.find(c => c.id === form.value.city)?.name ?? ''
  const stateNombre = deptos.value.find(d => d.id === form.value.state)?.name ?? ''
  const countryNombre = paises.value.find(c => c.id === form.value.country)?.name ?? ''
  const coords = await geocodificar(form.value.direccion, cityNombre, stateNombre, countryNombre)

  if (coords.length === 0) toast.warning('No se encontraron coordenadas. La sede se guardará sin GPS.')

  locates.value = coords
  askingLocates.value = false
}

function selectLocate(locate) {
  if (selectedLocate.value && locate.place_id === selectedLocate.value) {
    selectedLocate.value = null
    form.value.lat = null
    form.value.lng = null
    return
  }

  form.value.lat = locate.lat
  form.value.lng = locate.lon
  selectedLocate.value = locate.place_id
}

async function changeLocate() {
  form.value.lat = null
  form.value.lng = null

  await handleDireccion()
}

// ── Modales ────────────────────────────────────────
function openCreate() {
  form.value = { ...emptyForm(), negocio: negocioActivo.value }
  modal.value = { open: true, mode: 'create', item: null }
}
async function openEdit(item) {
  form.value = {
    ...item,
    status: item.status.value,
    negocio: item.negocio.nit,
    country: item.country?.id ?? '',
    state: item.state?.id ?? '',
    city: item.city?.id ?? '',
  }

  await getDeptos()
  await getCities()

  modal.value = { open: true, mode: 'edit', item }
}
function closeModal() { modal.value.open = false; locates.value = []; askingLocates.value = false }

// ── Guardar ────────────────────────────────────────
async function handleSubmit() {
  saving.value = true
  try {
    // const payload = {
    //   ...form.value,
    // }

    if (modal.value.mode === 'create') {
      await sedesApi.create(form.value)
      toast.success('Sede creada' + (hasCoords.value ? ' · Aparecerá en el mapa.' : ' · Sin GPS.'))
    } else {
      await sedesApi.update(modal.value.item.uuid, form.value)
      toast.success('Sede actualizada')
    }
    closeModal()
    const res = await sedesApi.list()
    sedes.value = res.data?.results ?? res.data ?? []
  } catch (err) {
    console.log(err)
    toast.error(err.response?.data ? Object.values(err.response.data).flat().join(' · ') : 'Error al guardar')
  } finally { saving.value = false }
}

// ── Eliminar ───────────────────────────────────────
async function editStatus(item) {
  const accion = item.status.value === 'Activo' ? 'Desactivar' : 'Activar'
  if (!confirm(`¿${accion} la sede "${item.nombre}"?`)) return

  try {
    const res = await sedesApi.editStatus(item.uuid, item.status.value === 'Activo' ? 'Inactivo' : 'Activo')
    toast.success(`Sede ${res.data?.status.value}`)

    const found = sedes.value.find(n => n.uuid === item.uuid)
    if (found) found.status.value = res.data?.status.value

  } catch { toast.error('No se pudo cambiar el estado') }
}

// ── Navegación ─────────────────────────────────────
const irPuestos = (sedeUuid) =>
  router.push({ name: 'puestos', params: { sede: sedeUuid } })
const irColaboradores = (uuid) => router.push({ name: 'colaboradores-sede', params: { uuid } })

function filterNegocios() {
  return negocios.value.filter(f => auth.can(modal.value.mode, 'negocios', f))
}
</script>

<template>
  <div class="p-6 max-w-screen-lg mx-auto">

    <!-- Header -->
    <div class="flex justify-between items-start mb-6">
      <div>
        <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Sedes</h1>
        <p class="text-t-secondary text-sm mt-1">
          Gestiona las sedes de cada negocio. Selecciona un negocio para comenzar.
        </p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus :size="15" /> Nueva sede
      </button>
    </div>

    <!-- ── Selector de negocio ── -->
    <div class="flex items-center gap-3 mb-6 p-4 card-dark rounded-lg">
      <div class="w-9 h-9 rounded-sm bg-accent/10 border border-accent/20 flex items-center justify-center shrink-0">
        <ParkingCircle :size="16" class="text-accent" />
      </div>
      <div class="flex-1">
        <div class="label-dark mb-1">NEGOCIO</div>
        <select class="input-dark" v-model="negocioActivo" :disabled="loadingNegocios">
          <option value="">Todas las sedes</option>
          <option v-for="n in negocios" :key="n.nit" :value="n.nit">
            {{ n.nombre }} · NIT {{ n.nit }}
          </option>
        </select>
      </div>
      <!-- Info del negocio seleccionado -->
      <div class="hidden md:flex flex-col items-end gap-1 shrink-0">
        <span class="text-xs text-t-muted">{{ sedesFiltradas.length }} sedes</span>
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="flex flex-col gap-3">
      <div v-for="i in 3" :key="i" class="skeleton h-24" />
    </div>

    <!-- Vacío -->
    <div v-else-if="sedesFiltradas.length === 0" class="card-dark rounded-lg py-16 text-center">
      <MapPin :size="40" class="text-t-muted mx-auto mb-3" :stroke-width="1" />
      <p class="font-head font-bold text-t-primary mb-1">Sin sedes registradas</p>
      <p class="text-sm text-t-secondary">Agrega la primera sede para este negocio.</p>
    </div>

    <!-- Lista de sedes -->
    <div v-else class="flex flex-col gap-3">
      <div v-for="s in sedesFiltradas" :key="s.uuid"
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
              <span :class="s.status.value === 'Activo' ? 'badge-green' : 'badge-red'">{{ s.status.value }}</span>
              <span v-if="s.lat && s.lng" class="inline-flex items-center gap-1 text-[10px] font-medium text-accent/70">
                <Navigation :size="9" /> GPS
              </span>
            </div>
            <div class="flex items-center gap-1 text-xs text-t-secondary">
              <MapPin :size="10" class="text-t-muted shrink-0" />
              <span class="truncate">{{ s.direccion }}</span>
            </div>
          </div>

          <!-- Stats rápidos -->
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
            <button v-if="auth.can('edit', 'sedes', s)" class="btn-icon w-8 h-8" title="Editar" @click="openEdit(s)">
              <Pencil :size="13" />
            </button>
            <button v-if="auth.can('manage_staff', 'sedes', s)" class="btn-icon w-7 h-7" title="Gestionar colaboradores"
              @click="irColaboradores(s.uuid)">
              <Users :size="12" />
            </button>
            <button v-if="auth.can('edit', 'sedes', s)" class="btn-icon w-7 h-7" :class="{
              'hover:text-danger hover:border-danger/30': s.status.value === 'Activo',
              'hover:text-accent hover:border-accent/30': s.status.value === 'Inactivo',
            }" :title="s.status.value === 'Activo' ? 'Desactivar' : 'Activar'" @click="editStatus(s)">
              <ThumbsUp :size="12" v-if="s.status.value === 'Inactivo'" />
              <ThumbsDown :size="12" v-else />
            </button>
            <button v-if="auth.can('manage_puestos', 'sedes', s)" class="btn-primary text-xs px-3 py-1.5 ml-1"
              @click="irPuestos(s.uuid)">
              <LandPlot :size="15" />
              Puestos
              <ChevronRight :size="12" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal crear/editar sede -->
    <CrudModal :open="modal.open" :title="modal.mode === 'create' ? 'Nueva sede' : 'Editar sede'"
      :loading="saving || askingLocates"
      :submit-label="saving ? 'Guardando...' : askingLocates ? 'Buscando coordenadas...' : 'Guardar sede'" size="lg"
      @close="closeModal" @submit="handleSubmit">

      <div class="overflow-y-auto max-h-[60vh]">
        <div>
          <label class="label-dark">NOMBRE DE LA SEDE</label>
          <input class="input-dark" v-model="form.nombre" placeholder="Ej: Sede Norte, Sede Chapinero" required />
        </div>

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
            <select class="input-dark" v-model="form.state" @change="onDeptoChange" required :disabled="!deptos.length">
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

        <div>
          <label class="label-dark">DIRECCIÓN</label>
          <div class="relative">
            <input class="input-dark pr-10" v-model="form.direccion" placeholder="Calle 26 # 13-20" required
              @blur="handleDireccion" @change="handleDireccion" />
          </div>
          <div v-if="hasCoords" class="mt-1.5 ml-3 flex items-center gap-1.5 text-xs text-blue">
            <MapPin :size="15" />
            <span class="font-mono">{{ form.lat }}, {{ form.lng }}</span>
            <span class="text-t-secondary">— Aparecerá en el mapa</span>
            <button class="btn-icon w-8 h-8 ml-auto hover:border-blue hover:text-blue" title="Cambiar ubicación"
              @click="changeLocate">
              <RefreshCcwDot :size="12" />
            </button>
          </div>

          <p v-else-if="askingLocates" class="mt-1 ml-3 text-xs text-t-muted">
            Buscando coordenadas...
          </p>

          <div v-else-if="locates.length > 0 && form.direccion"
            class="mt-1.5 flex flex-col ml-3 max-h-40 overflow-y-auto gap-3 text-xs text-t-secondary">
            <div v-for="locate in locates" :key="locate.place_id" class="flex items-center gap-2 border p-2 border-[var(--t-secondary)] rounded-sm hover:cursor-pointer
              hover:border-blue hover:text-blue" :class="{
                'border-accent text-accent': selectedLocate === locate.place_id,
                'opacity-60': selectedLocate && selectedLocate !== locate.place_id
              }" @click="selectLocate(locate)">
              <MapPin :size="30" />
              <span class="font-mono">{{ locate.display_name }}</span>
            </div>
          </div>

          <p v-else class="mt-1 ml-3 text-xs text-t-muted">
            Las coordenadas GPS se detectan al salir del campo. Puedes continuar sin ellas.
          </p>
        </div>

        <div>
          <select class="input-dark" v-model="form.negocio" required>
            <option value="">Selecciona un negocio</option>
            <option v-for="n in filterNegocios()" :key="n.nit" :value="n.nit">
              {{ n.nombre }} · NIT {{ n.nit }}
            </option>
          </select>
        </div>

        <!-- MINUTOS DE GRACIA -->
        <div v-if="modal.mode === 'edit'">
          <label class="label-dark">
            MINUTOS DE GRACIA
          </label>
          <p class="text-xs text-t-secondary mb-1">
            Tiempo en minutos de cortesía antes de cobrar la primera fracción
          </p>
          <input class="input-dark" v-model="form.minutos_gracia" type="number" min="0" placeholder="Ej: 5" />
        </div>
      </div>
    </CrudModal>

  </div>
</template>
