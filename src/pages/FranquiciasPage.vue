<script setup>
/**
 * FranquiciasPage.vue
 *
 * Cambios respecto a versión anterior:
 *  - Botón "Gestionar negocios" prominente (como "Gestionar sedes" en NegociosPage)
 *  - Se mueve al footer de la tarjeta/fila
 *  - La tabla muestra también la razón social y NIT de forma más limpia
 *  - Negocios count añadido cuando esté disponible
 */
import { ref, onMounted } from 'vue'
import { Plus, Pencil, ThumbsDown, ThumbsUp, Building2, Users, ChevronRight, ParkingCircle, MapPin, BuildingIcon, Building2Icon } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import CrudModal from '@/components/CrudModal.vue'
import { franquiciasApi } from '@/api/axios'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const toast  = useToast()
const auth   = useAuthStore()

const items   = ref([])
const loading = ref(true)
const saving  = ref(false)
const modal   = ref({ open: false, mode: 'create', item: null })

// Count de negocios por franquicia
const emptyForm = () => ({
  nit: '', numero_verificacion: '', razon_social: '', nombre: '',
  creado_por: auth.user?.numero_id ?? '',
})
const form = ref(emptyForm())

onMounted(fetchAll)

async function fetchAll() {
  loading.value = true
  try {
    const res = await franquiciasApi.list()
    items.value = res.data?.results ?? res.data ?? []

  } finally { loading.value = false }
}

function openCreate() {
  form.value = emptyForm()
  modal.value = { open: true, mode: 'create', item: null }
}
function openEdit(item) {
  form.value  = { ...item }
  modal.value = { open: true, mode: 'edit', item }
}
function closeModal() { modal.value.open = false }

async function handleSubmit() {
  saving.value = true
  try {
    if (modal.value.mode === 'create') {
      await franquiciasApi.create(form.value)
      toast.success('Franquicia creada')
    } else {
      await franquiciasApi.update(modal.value.item.uuid, form.value)
      toast.success('Franquicia actualizada')
    }
    closeModal()
    await fetchAll()
  } catch (err) {
    toast.error(err.response?.data ? Object.values(err.response.data).flat().join(' · ') : 'Error al guardar')
  } finally { saving.value = false }
}

async function editStatus(item) {
  const accion = item.status === 'Activo' ? 'Desactivar' : 'Activar'
  if (!confirm(`¿${accion} la franquicia "${item.nombre}"?`)) return
  try {
    const res = await franquiciasApi.editStatus(item.uuid, item.status === 'Activo' ? 'Inactivo' : 'Activo')
    toast.success(`Franquicia ${res.data?.status}`)
    const found = items.value.find(f => f.uuid === item.uuid)
    if (found) found.status = res.data?.status
  } catch { toast.error('No se pudo cambiar el estado') }
}

// ── Navegación ──────────────────────────────────────────────
// "Gestionar negocios" → /negocios?franquicia=uuid (NegociosPage pre-filtrada)
const irNegocios      = (uuid) => router.push({ name: 'negocios', query: { franquicia: uuid } })
const irColaboradores = (uuid) => router.push({ name: 'colaboradores-franquicia', params: { uuid } })
</script>

<template>
  <div class="p-6 max-w-screen-lg mx-auto">

    <!-- Header -->
    <div class="flex justify-between items-start mb-7">
      <div>
        <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Franquicias</h1>
        <p class="text-t-secondary text-sm mt-1">
          Empresas holding que agrupan múltiples negocios. Haz clic en → para gestionar sus negocios.
        </p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus :size="15" /> Nueva franquicia
      </button>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="i in 4" :key="i" class="skeleton h-32" />
    </div>

    <!-- Vacío -->
    <div v-else-if="items.length === 0" class="card-dark rounded-lg py-16 text-center">
      <Building2 :size="40" class="text-t-muted mx-auto mb-3" :stroke-width="1" />
      <p class="font-head font-bold text-t-primary mb-1">Sin franquicias</p>
      <p class="text-sm text-t-secondary">Crea tu primera franquicia para agrupar tus negocios.</p>
    </div>

    <!-- Grid de tarjetas (espejo de NegociosPage) -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="item in items" :key="item.uuid"
           class="card-dark rounded-lg overflow-hidden hover:border-border-hover transition-all animate-fade-up">

        <!-- Top: nombre + badge estado -->
        <div class="flex items-start justify-between p-4 pb-3">
          <div class="flex items-start gap-3 flex-1 min-w-0">
            <div class="w-9 h-9 rounded-sm bg-purple/10 border border-purple/20 flex items-center justify-center shrink-0">
              <Building2 :size="16" class="text-purple" />
            </div>
            <div class="min-w-0">
              <div class="font-head font-bold text-t-primary text-sm leading-tight truncate">
                {{ item.nombre }}
              </div>
              <!-- NIT + Razón social (antes estaban en columnas separadas) -->
              <div class="text-[11px] text-t-muted mt-0.5 truncate">
                <span v-if="item.nit" class="font-mono">NIT {{ item.nit }}<span v-if="item.numero_verificacion">-{{ item.numero_verificacion }}</span></span>
                <span v-if="item.nit && item.razon_social" class="mx-1">·</span>
                <span v-if="item.razon_social">{{ item.razon_social }}</span>
                <span v-if="!item.nit && !item.razon_social" class="italic">Sin información fiscal</span>
              </div>
            </div>
          </div>
          <span :class="item.status === 'Activo' ? 'badge-green' : 'badge-red'" class="shrink-0 ml-2">
            {{ item.status }}
          </span>
        </div>

        <!-- Stats: Negocios + Colaboradores (datos que sí tenemos) -->
        <div class="grid grid-cols-2 gap-px bg-border mx-4 rounded-sm overflow-hidden mb-3">
          <div class="bg-input px-3 py-2 text-center">
            <div class="text-[10px] text-t-muted uppercase tracking-wider mb-0.5">Negocios</div>
            <div class="font-head font-bold text-purple text-sm">
              {{ item.negocios_count ?? '—' }}
            </div>
          </div>
          <div class="bg-input px-3 py-2 text-center">
            <div class="text-[10px] text-t-muted uppercase tracking-wider mb-0.5">Estado</div>
            <div class="text-sm font-semibold"
                 :class="item.status === 'Activo' ? 'text-accent' : 'text-danger'">
              {{ item.status }}
            </div>
          </div>
        </div>

        <!-- Footer acciones (espejo de NegociosPage) -->
        <div class="flex items-center justify-between px-4 py-3 border-t border-border bg-surface/30">
          <div class="flex gap-1">
            <button class="btn-icon w-7 h-7" title="Editar franquicia" @click="openEdit(item)">
              <Pencil :size="12" />
            </button>
            <button class="btn-icon w-7 h-7" title="Gestionar colaboradores"
                    @click="irColaboradores(item.uuid)">
              <Users :size="12" />
            </button>
            <button class="btn-icon w-7 h-7"
                    :class="{
                      'hover:text-danger hover:border-danger/30': item.status === 'Activo',
                      'hover:text-accent hover:border-accent/30': item.status === 'Inactivo',
                    }"
                    :title="item.status === 'Activo' ? 'Desactivar' : 'Activar'"
                    @click="editStatus(item)">
              <ThumbsUp :size="12" v-if="item.status === 'Inactivo'" />
              <ThumbsDown :size="12" v-else />
            </button>
          </div>

          <!-- ← Botón "Gestionar negocios" prominente (como "Gestionar sedes" en NegociosPage) -->
          <button class="flex items-center gap-1.5 text-xs text-accent hover:underline font-medium"
                  @click="irNegocios(item.uuid)">
            <ParkingCircle :size="12" /> Gestionar negocios <ChevronRight :size="12" />
          </button>
        </div>
      </div>
    </div>

    <!-- Modal crear/editar franquicia -->
    <CrudModal :open="modal.open"
               :title="modal.mode === 'create' ? 'Nueva franquicia' : 'Editar franquicia'"
               :loading="saving" @close="closeModal" @submit="handleSubmit">
      <div>
        <label class="label-dark">NOMBRE VISIBLE EN LA APP</label>
        <input class="input-dark" v-model="form.nombre"
               placeholder="Ej: Parkings del Norte S.A.S" required />
      </div>
      <div>
        <label class="label-dark">RAZÓN SOCIAL</label>
        <input class="input-dark" v-model="form.razon_social"
               placeholder="Razón social completa" />
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="label-dark">NIT</label>
          <input class="input-dark" v-model="form.nit" placeholder="900123456" />
        </div>
        <div>
          <label class="label-dark">DÍG. VERIFICACIÓN</label>
          <input class="input-dark" type="number" v-model="form.numero_verificacion" placeholder="7" />
        </div>
      </div>
    </CrudModal>

  </div>
</template>
