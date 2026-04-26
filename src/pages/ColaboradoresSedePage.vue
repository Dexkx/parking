<script setup>
/**
 * ColaboradoresNegocioPage.vue
 * Gestión completa de colaboradores de un negocio.
 * Ruta: /negocios/:nit/colaboradores
 *
 * Funciones:
 *  - Listar colaboradores con su tipo (Dueño, Admin, Trabajador)
 *  - Agregar nuevo colaborador (usuario + tipo)
 *  - Editar tipo de colaborador existente
 *  - Eliminar colaborador
 */
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Plus, Pencil, Trash2, Users, ParkingCircle, MapPin } from 'lucide-vue-next'
import CrudModal from '@/components/CrudModal.vue'
import { sedesApi, catalogosApi } from '@/api/axios'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'

const route  = useRoute()
const router = useRouter()
const toast  = useToast()
const auth   = useAuthStore()

const uuid    = route.params.uuid
const sede    = ref(null)
const items   = ref([])
const tipos   = ref([])
const loading = ref(true)
const saving  = ref(false)

// Modal unificado: crear o editar
const modal = ref({ open: false, mode: 'create', item: null })

const emptyForm = () => ({ usuario: '', tipo_colaborador: '' })
const form = ref(emptyForm())

onMounted(async () => {
  const [sedRes, colRes, tiposRes] = await Promise.all([
    sedesApi.get(uuid),
    sedesApi.colaboradores(uuid),
    catalogosApi.tiposColaborador(),
  ])
  sede.value    = sedRes.data?.results ?? sedRes.data ?? null
  items.value   = colRes.data?.results   ?? colRes.data   ?? []
  tipos.value   = tiposRes.data?.results ?? tiposRes.data ?? []
  loading.value = false
})

// ── Abrir modales ──────────────────────────
function openCreate() {
  form.value = emptyForm()
  modal.value = { open: true, mode: 'create', item: null }
}

function openEdit(col) {
  form.value = {
    usuario:          col.usuario?.numero_id ?? col.usuario,
    tipo_colaborador: col.tipo_colaborador?.code ?? col.tipo_colaborador,
  }
  modal.value = { open: true, mode: 'edit', item: col }
}

function closeModal() { modal.value.open = false }

// ── Acciones CRUD ──────────────────────────
async function handleSubmit() {
  saving.value = true
  try {
    if (modal.value.mode === 'create') {
      await sedesApi.addColaborador(uuid, form.value)
      toast.success('Colaborador agregado correctamente')
    } else {
      const userId = modal.value.item?.usuario?.numero_id ?? modal.value.item?.usuario
      await sedesApi.editColaborador(uuid, userId, { tipo_colaborador: form.value.tipo_colaborador })
      toast.success('Tipo de colaborador actualizado')
    }
    closeModal()
    const res = await sedesApi.colaboradores(uuid)
    items.value = res.data?.results ?? res.data ?? []
  } catch (err) {
    const data = err.response?.data
    const msg  = data ? Object.values(data).flat().join(' · ') : 'Error al guardar'
    toast.error(msg)
  } finally { saving.value = false }
}

async function handleDelete(col) {
  const nombre = col.usuario?.nombre ?? col.usuario?.numero_id ?? 'este colaborador'
  if (!confirm(`¿Eliminar a "${nombre}" del negocio?`)) return
  try {
    const userId = col.usuario?.numero_id ?? col.usuario
    await sedesApi.removeColaborador(uuid, userId)
    toast.success('Colaborador eliminado')
    items.value = items.value.filter(c =>
      (c.usuario?.numero_id ?? c.usuario) !== userId
    )
  } catch { toast.error('No se pudo eliminar. Verifica permisos.') }
}

// ── Helpers visuales ───────────────────────
const TIPO_BADGES = {
  '-1': 'badge-purple',  // Dueño
  '0':  'badge-blue',    // Administrador
  '1':  'badge-green',   // Trabajador
}

function badgeColaborador(col) {
  const code = col.tipo_colaborador?.code ?? col.tipo_colaborador
  return TIPO_BADGES[code] ?? 'badge-blue'
}

function labelColaborador(col) {
  return col.tipo_colaborador?.descripcion ?? col.tipo_colaborador ?? '—'
}

const inicial = (col) =>
  (col.usuario?.nombre ?? col.usuario?.numero_id ?? '?').charAt(0).toUpperCase()

function tipos_colab_filtering() {
  const role = auth.getRole('sedes', sede.value)

  let tipos_available = tipos.value.filter(t => t.code !== '-1')

  switch (role) {
    case '1':
      tipos_available = []
      break
    case '0':
      tipos_available = tipos_available.filter(t => t.code !== '0')
      break
    default:
      break
  }

  return tipos_available
}

function can_action(action, tipo_colab) {
  const role = auth.getRole('sedes', sede.value)
  if (role === '-1') return true
  if (tipo_colab === '-1' || !tipo_colab) return false

  switch (action) {
    case 'edit':
      return false
    case 'delete':
      return role === '0' && tipo_colab !== '0'
  }
}
</script>

<template>
  <div class="p-6 max-w-screen-md mx-auto">

    <!-- Back -->
    <button class="flex items-center gap-1.5 text-xs text-t-muted hover:text-t-primary transition-colors mb-5"
            @click="router.back()">
      <ArrowLeft :size="13" /> Volver a sedes
    </button>

    <!-- Header -->
    <div class="flex justify-between items-start mb-7">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <MapPin :size="20" class="text-blue" />
          <div class="flex flex-col">
            <span class="text-xs text-t-secondary font-medium">{{ sede?.nombre ?? uuid }}</span>
            <span class="text-xs text-t-muted font-medium italic">{{ sede?.lat }}, {{ sede?.lng }}</span>
          </div>
        </div>
        <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Colaboradores</h1>
        <p class="text-t-secondary text-sm mt-1">
          Empleados con acceso a la gestión de la sede.
        </p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus :size="15" /> Agregar colaborador
      </button>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="flex flex-col gap-3">
      <div v-for="i in 4" :key="i" class="skeleton h-16" />
    </div>

    <!-- Vacío -->
    <div v-else-if="items.length === 0" class="card-dark rounded-lg py-16 text-center">
      <Users :size="40" class="text-t-muted mx-auto mb-3" :stroke-width="1" />
      <p class="font-head font-bold text-t-primary mb-1">Sin colaboradores</p>
      <p class="text-sm text-t-secondary">Agrega personas para que puedan gestionar este negocio.</p>
    </div>

    <!-- Lista -->
    <div v-else class="card-dark rounded-lg overflow-hidden">

      <!-- Header tabla -->
      <div class="grid grid-cols-[auto_1fr_1fr_120px] bg-surface/50 border-b border-border">
        <div class="table-head-cell pl-4 w-12"></div>
        <div class="table-head-cell">Nombre / ID</div>
        <div class="table-head-cell">Rol</div>
        <div class="table-head-cell text-right pr-4">Acciones</div>
      </div>

      <div v-for="col in items" :key="col.usuario?.numero_id ?? col.usuario"
           class="grid grid-cols-[auto_1fr_1fr_120px] border-b border-border last:border-0 hover:bg-card-hover transition-colors">

        <!-- Avatar -->
        <div class="flex items-center pl-4 py-3 w-12">
          <div class="w-8 h-8 rounded-full bg-blue/10 border border-blue/20 flex items-center justify-center text-blue text-xs font-bold font-head shrink-0">
            {{ inicial(col) }}
          </div>
        </div>

        <!-- Nombre + ID -->
        <div class="flex flex-col justify-center ml-4 py-3 min-w-0">
          <span class="font-medium text-t-primary text-sm truncate">
            {{ col.usuario?.nombre ?? '—' }}
          </span>
          <span class="font-mono text-[11px] text-t-muted">
            {{ col.usuario?.numero_id ?? col.usuario }}
          </span>
        </div>

        <!-- Badge tipo -->
        <div class="flex items-center py-3">
          <span :class="badgeColaborador(col)">{{ labelColaborador(col) }}</span>
        </div>

        <!-- Acciones -->
        <div class="flex items-center justify-end gap-1.5 pr-4 py-3">
          <!-- No editar/eliminar al Dueño (-1) -->
          <template v-if="(col.tipo_colaborador?.code ?? col.tipo_colaborador) !== '-1'">
            <button class="btn-icon w-7 h-7" title="Cambiar rol"
              v-if="can_action('edit', col.tipo_colaborador?.code)"
              @click="openEdit(col)">
              <Pencil :size="12" />
            </button>
            <button class="btn-icon w-7 h-7 hover:text-danger hover:border-danger/30"
              v-if="can_action('delete', col.tipo_colaborador?.code)"
              title="Eliminar" @click="handleDelete(col)">
              <Trash2 :size="12" />
            </button>
          </template>
          <span v-else class="text-[11px] text-t-muted italic px-1">Propietario</span>
        </div>
      </div>
    </div>

    <!-- Info de roles -->
    <div class="grid grid-cols-3 gap-3 mt-5">
      <div v-for="r in [
        { label: 'Dueño', desc: 'Acceso total. No puede ser eliminado.', badge: 'badge-purple' },
        { label: 'Administrador', desc: 'Gestiona sedes, puestos y clientes.', badge: 'badge-blue' },
        { label: 'Trabajador', desc: 'Solo puede ver reservas y clientes.', badge: 'badge-green' },
      ]" :key="r.label"
         class="bg-input/50 rounded-lg p-3 border border-border text-xs">
        <span :class="[r.badge, 'mb-1.5 inline-flex']">{{ r.label }}</span>
        <p class="text-t-muted">{{ r.desc }}</p>
      </div>
    </div>

    <!-- Modal crear/editar colaborador -->
    <CrudModal
      :open="modal.open"
      :title="modal.mode === 'create' ? 'Agregar colaborador' : 'Cambiar rol'"
      :loading="saving"
      :submit-label="modal.mode === 'create' ? 'Agregar' : 'Guardar cambio'"
      @close="closeModal"
      @submit="handleSubmit"
    >
      <!-- Solo se puede cambiar el usuario al crear -->
      <div v-if="modal.mode === 'create'">
        <label class="label-dark">N° IDENTIFICACIÓN DEL USUARIO</label>
        <input class="input-dark" v-model="form.usuario"
               placeholder="Ej: 1234567890" required
               autofocus />
        <p class="text-xs text-t-muted mt-1.5">
          El usuario debe tener cuenta activa en ParkApp.
        </p>
      </div>

      <!-- En edición solo se cambia el tipo -->
      <div v-else class="bg-input/50 rounded-sm p-3 border border-border text-xs text-t-muted mb-1">
        Cambiando rol de
        <span class="text-t-primary font-semibold">
          {{ modal.item?.usuario?.nombre ?? modal.item?.usuario?.numero_id ?? '—' }}
        </span>
      </div>

      <div>
        <label class="label-dark">ROL / TIPO DE COLABORADOR</label>
        <select class="input-dark" v-model="form.tipo_colaborador" required>
          <option value="">Selecciona un rol</option>
          <option v-for="t in tipos_colab_filtering()"
                  :key="t.code" :value="t.code">
            {{ t.descripcion }}
          </option>
        </select>
      </div>
    </CrudModal>

  </div>
</template>
