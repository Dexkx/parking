<script setup>
/**
 * NegociosPage.vue
 *
 * Cambios respecto a versión anterior:
 *  - Selector de franquicia en la parte superior (filtra la lista)
 *  - Pre-selecciona franquicia si viene ?franquicia=uuid en la URL
 *  - Quita la stat "Ciudad" de las tarjetas (queda Sedes + Puntuación)
 *  - "Gestionar sedes" navega a /sedes?negocio=nit (SedesGeneralPage)
 *  - "Colaboradores" navega a /negocios/:nit/colaboradores
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, Pencil, ThumbsDown, ThumbsUp, ParkingCircle, MapPin, ChevronRight, Users, Building2, DollarSign } from 'lucide-vue-next'
import CrudModal from '@/components/CrudModal.vue'
import { negociosApi, franquiciasApi } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const route = useRoute()
const router = useRouter()
const toast  = useToast()
const auth   = useAuthStore()

const items          = ref([])   // todos los negocios
const franquicias    = ref([])
const franqActiva    = ref(route.query.franquicia ?? '')   // uuid de franquicia seleccionada ('' = todas)

const loading        = ref(true)
const saving         = ref(false)
const modal          = ref({ open: false, mode: 'create', item: null })

const emptyForm = () => ({
  nit: '', numero_verificacion: '', razon_social: '', nombre: '',
  creado_por: auth.user?.numero_id ?? '', franquicia: franqActiva.value ?? ''
})
const form = ref(emptyForm())

// ── Filtrado por franquicia ─────────────────────────────────
const negociosFiltrados = computed(() => {
  router.push(franqActiva.value ? { query: { franquicia: franqActiva.value } } : {})

  if (!franqActiva.value) return items.value

  return items.value.filter(n => n.franquicia?.uuid === franqActiva.value)
})

// ── Carga inicial ───────────────────────────────────────────
onMounted(async () => {
  loading.value = true
  const [negRes, franqRes] = await Promise.all([
    negociosApi.list(),
    franquiciasApi.list(),
  ])
  items.value      = negRes.data?.results   ?? negRes.data   ?? []
  franquicias.value = franqRes.data?.results ?? franqRes.data ?? []
  loading.value = false
})

// ── CRUD Negocios ───────────────────────────────────────────
function openCreate() {
  form.value = emptyForm()
  modal.value = { open: true, mode: 'create', item: null }
}
function openEdit(item) {
  form.value  = { ...item, creado_por: item.creado_por ?? auth.user?.numero_id, franquicia: item.franquicia?.uuid, status: item.status.value }
  modal.value = { open: true, mode: 'edit', item }
}
function closeModal() { modal.value.open = false }

async function handleSubmit() {
  saving.value = true
  try {
    if (modal.value.mode === 'create') {
      await negociosApi.create(form.value)
      toast.success('Negocio creado. Ahora agrega sus sedes.')
    } else {
      await negociosApi.update(modal.value.item.nit, form.value)
      toast.success('Negocio actualizado')
    }
    closeModal()
    const res = await negociosApi.list()
    items.value = res.data?.results ?? res.data ?? []
  } catch (err) {
    toast.error(err.response?.data ? Object.values(err.response.data).flat().join(' · ') : 'Error al guardar')
  } finally { saving.value = false }
}

async function editStatus(item) {
  const accion = item.status.value === 'Activo' ? 'Desactivar' : 'Activar'
  if (!confirm(`¿${accion} el negocio "${item.nombre}"?`)) return
  try {
    const res = await negociosApi.editStatus(item.nit, item.status.value === 'Activo' ? 'Inactivo' : 'Activo')
    toast.success(`Negocio ${res.data?.status.value}`)
    const found = items.value.find(n => n.nit === item.nit)
    if (found) found.status.value = res.data?.status.value
  } catch { toast.error('No se pudo cambiar el estado') }
}

// ── Navegación ──────────────────────────────────────────────
// Sedes → va a la página general de sedes filtrada por este negocio
const irSedes         = (nit) => router.push({ name: 'sedes-general', query: { negocio: nit } })
const irColaboradores = (nit) => router.push({ name: 'colaboradores-negocio', params: { nit } })
const irTarifas       = (nit) => router.push({ name: 'tarifas-negocio', params: { nit } })

function filterFranquicas() {
  return franquicias.value.filter(f => auth.can(modal.value.mode, 'franquicias', f))
}
</script>

<template>
  <div class="p-6 max-w-screen-lg mx-auto">

    <!-- Header -->
    <div class="flex justify-between items-start mb-6">
      <div>
        <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Negocios</h1>
        <p class="text-t-secondary text-sm mt-1">
          Cada negocio puede tener múltiples sedes. Usa el filtro para ver por franquicia.
        </p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus :size="15" /> Nuevo negocio
      </button>
    </div>

    <!-- ── Filtro por franquicia ── -->
    <div class="flex items-center gap-3 mb-5 p-4 card-dark rounded-lg">
      <div class="w-9 h-9 rounded-sm bg-purple/10 border border-purple/20 flex items-center justify-center shrink-0">
        <Building2 :size="16" class="text-purple" />
      </div>
      <div class="flex-1">
        <div class="label-dark mb-1">FILTRAR POR FRANQUICIA</div>
        <select class="input-dark" v-model="franqActiva">
          <option value="">Todos los negocios</option>
          <option v-for="f in franquicias" :key="f.uuid" :value="f.uuid">{{ f.nombre }}</option>
        </select>
      </div>
      <div class="shrink-0 text-xs text-t-muted">
        {{ negociosFiltrados.length }} negocio{{ negociosFiltrados.length !== 1 ? 's' : '' }}
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="i in 4" :key="i" class="skeleton h-32" />
    </div>

    <!-- Vacío -->
    <div v-else-if="negociosFiltrados.length === 0" class="card-dark rounded-lg py-16 text-center">
      <ParkingCircle :size="40" class="text-t-muted mx-auto mb-3" :stroke-width="1" />
      <p class="font-head font-bold text-t-primary mb-1">Sin negocios</p>
      <p class="text-sm text-t-secondary">
        {{ franqActiva ? 'Esta franquicia no tiene negocios asignados.' : 'Registra tu primer parqueadero para comenzar.' }}
      </p>
    </div>

    <!-- Grid de tarjetas -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="n in negociosFiltrados" :key="n.nit"
           class="card-dark rounded-lg overflow-hidden hover:border-border-hover transition-all animate-fade-up">

           <!-- Top -->
        <div class="flex items-start justify-between p-4 pb-3">
          <div class="flex items-start gap-3 flex-1 min-w-0">
            <div class="w-9 h-9 rounded-sm bg-accent/10 border border-accent/20 flex items-center justify-center shrink-0">
              <ParkingCircle :size="16" class="text-accent" />
            </div>
            <div class="min-w-0">
              <div class="font-head font-bold text-t-primary text-sm leading-tight truncate">{{ n.nombre }}</div>
              <div class="font-mono text-[11px] text-t-muted mt-0.5">NIT {{ n.nit }}-{{ n.numero_verificacion }}</div>
            </div>
          </div>
          <div class="flex items-center gap-2 shrink-0 ml-2">
            <button class="btn-ghost px-2 py-0.5 text-[11px] h-6" title="Tarifas generales"
                    @click="irTarifas(n.nit)">
              <DollarSign :size="12" /> Tarifas
            </button>
            <span :class="n.status.value === 'Activo' ? 'badge-green' : 'badge-red'" class="text-[10px] uppercase font-bold shrink-0">
              {{ n.status.value }}
            </span>
          </div>
        </div>

        <!-- Stats: solo Sedes y Puntuación (sin Ciudad) -->
        <div class="grid grid-cols-2 gap-px bg-border mx-4 rounded-sm overflow-hidden mb-3">
          <div class="bg-input px-3 py-2 text-center">
            <div class="text-[10px] text-t-muted uppercase tracking-wider mb-0.5">Sedes</div>
            <div class="font-head font-bold text-accent text-sm">{{ n.sedes_count ?? 0 }}</div>
          </div>
          <div class="bg-input px-3 py-2 text-center">
            <div class="text-[10px] text-t-muted uppercase tracking-wider mb-0.5">Puntuación</div>
            <div class="font-head font-bold text-warn text-sm">
              {{ n.puntuacion ? Number(n.puntuacion).toFixed(1) : '—' }} ★
            </div>
          </div>
        </div>

        <!-- Footer acciones -->
        <div class="flex items-center justify-between px-4 py-3 border-t border-border bg-surface/30">
          <div class="flex gap-1">
            <button class="btn-icon w-7 h-7" title="Editar negocio"
              v-if="auth.can('edit','negocios', n)" @click="openEdit(n)">
              <Pencil :size="12" />
            </button>
            <button class="btn-icon w-7 h-7" title="Gestionar colaboradores"
                v-if="auth.can('manage_staff','negocios', n)"
                @click="irColaboradores(n.nit)">
              <Users :size="12" />
            </button>
            <button class="btn-icon w-7 h-7"
                    :class="{
                      'hover:text-danger hover:border-danger/30': n.status.value === 'Activo',
                      'hover:text-accent hover:border-accent/30': n.status.value === 'Inactivo',
                    }"
                    :title="n.status.value === 'Activo' ? 'Desactivar' : 'Activar'"
                    v-if="auth.can('edit','negocios', n)"
                    @click="editStatus(n)">
              <ThumbsUp :size="12" v-if="n.status.value === 'Inactivo'" />
              <ThumbsDown :size="12" v-else />
            </button>
          </div>

          <!-- ← Navega a /sedes?negocio=nit -->
          <button class="flex items-center gap-1.5 text-xs text-accent hover:underline font-medium"
                  @click="irSedes(n.nit)">
            <MapPin :size="12" /> Gestionar sedes <ChevronRight :size="12" />
          </button>
        </div>
      </div>
    </div>

    <!-- Modal crear/editar negocio -->
    <CrudModal :open="modal.open"
               :title="modal.mode === 'create' ? 'Nuevo negocio' : 'Editar negocio'"
               :loading="saving" size="lg" @close="closeModal" @submit="handleSubmit">
      <div class="grid grid-cols-2 gap-3">
        <div class="col-span-2">
          <label class="label-dark">NOMBRE VISIBLE EN LA APP</label>
          <input class="input-dark" v-model="form.nombre"
                 placeholder="Ej: Parking Centro Internacional" required />
        </div>
        <div>
          <label class="label-dark">NIT</label>
          <input class="input-dark" v-model="form.nit"
                 placeholder="900123456" required
                 :disabled="modal.mode === 'edit'" />
        </div>
        <div>
          <label class="label-dark">DÍG. VERIFICACIÓN</label>
          <input class="input-dark" type="number" v-model="form.numero_verificacion"
                 placeholder="7" required />
        </div>
        <div class="col-span-2">
          <label class="label-dark">RAZÓN SOCIAL</label>
          <input class="input-dark" v-model="form.razon_social"
                 placeholder="Razón social completa" required />
        </div>
        <div class="col-span-2">
          <label for="franquicia" class="label-dark">FRANQUICIA</label>
          <select id="franquicia" class="input-dark" v-model="form.franquicia">
            <option value="">Selecciona una franquicia</option>
            <option v-for="f in filterFranquicas()" :key="f.uuid" :value="f.uuid">{{ f.nombre }}</option>
          </select>
        </div>
      </div>
    </CrudModal>

  </div>
</template>
