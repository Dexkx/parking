<script setup>
/**
 * NegociosPage.vue
 * CRUD de negocios. El botón de colaboradores ahora navega
 * a /negocios/:nit/colaboradores en vez de abrir un modal.
 */
import { ref, onMounted } from 'vue'
import { Plus, Pencil, ThumbsDown, ThumbsUp, ParkingCircle, MapPin, ChevronRight, Users, ThumbsUpIcon } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import CrudModal from '@/components/CrudModal.vue'
import { negociosApi } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const router = useRouter()
const toast  = useToast()
const auth   = useAuthStore()

const items   = ref([])
const loading = ref(true)
const saving  = ref(false)
const modal   = ref({ open: false, mode: 'create', item: null })

const emptyForm = () => ({
  nit: '', numero_verificacion: '', razon_social: '', nombre: '',
  creado_por: auth.user?.numero_id ?? '',
})
const form = ref(emptyForm())

onMounted(async () => {
  loading.value = true
  const res = await negociosApi.list()
  items.value  = res.data?.results ?? res.data ?? []
  loading.value = false
})

function openCreate() {
  form.value = emptyForm()
  modal.value = { open: true, mode: 'create', item: null }
}
function openEdit(item) {
  form.value  = { ...item, creado_por: item.creado_por ?? auth.user?.numero_id }
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
    const msg = err.response?.data
      ? Object.values(err.response.data).flat().join(' · ')
      : 'Error al guardar'
    toast.error(msg)
  } finally { saving.value = false }
}

async function editStatus(item) {
  if (!confirm(`¿Desactivar el negocio "${item.nombre}"? Será como eliminar el negocio, sus clientes no podrán acceder a él.`)) return
  try {
    const res = await negociosApi.editStatus(item.nit, item.status === 'Activo' ? 'Inactivo' : 'Activo')
    toast.success(`Negocio ${res.data?.status}`)
    const itemUpdate = items.value.find(n => n.nit === item.nit)
    itemUpdate.status = res.data?.status
  } catch { toast.error('No se pudo eliminar') }
}

// ── Navegación ──────────────────────────────────────────────
const irSedes         = (nit) => router.push({ name: 'sedes',                  params: { nit } })
const irColaboradores = (nit) => router.push({ name: 'colaboradores-negocio',  params: { nit } })
</script>

<template>
  <div class="p-6 max-w-screen-lg mx-auto">

    <!-- Header -->
    <div class="flex justify-between items-start mb-7">
      <div>
        <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Negocios</h1>
        <p class="text-t-secondary text-sm mt-1">
          Cada negocio puede tener múltiples sedes. Haz clic en → para gestionar sus sedes.
        </p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus :size="15" /> Nuevo negocio
      </button>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="i in 4" :key="i" class="skeleton h-32" />
    </div>

    <!-- Vacío -->
    <div v-else-if="items.length === 0" class="card-dark rounded-lg py-16 text-center">
      <ParkingCircle :size="40" class="text-t-muted mx-auto mb-3" :stroke-width="1" />
      <p class="font-head font-bold text-t-primary mb-1">Sin negocios</p>
      <p class="text-sm text-t-secondary">Registra tu primer parqueadero para comenzar.</p>
    </div>

    <!-- Grid de tarjetas -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="n in items" :key="n.nit"
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
          <span :class="n.status === 'Activo' ? 'badge-green' : 'badge-red'" class="shrink-0 ml-2">
            {{ n.status }}
          </span>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-3 gap-px bg-border mx-4 rounded-sm overflow-hidden mb-3">
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
          <div class="bg-input px-3 py-2 text-center">
            <div class="text-[10px] text-t-muted uppercase tracking-wider mb-0.5">Ciudad</div>
            <div class="text-t-secondary text-xs truncate">{{ n.ciudad?.name ?? '—' }}</div>
          </div>
        </div>

        <!-- Footer acciones -->
        <div class="flex items-center justify-between px-4 py-3 border-t border-border bg-surface/30">
          <div class="flex gap-1">
            <button class="btn-icon w-7 h-7" title="Editar negocio" @click="openEdit(n)">
              <Pencil :size="12" />
            </button>
            <!-- ← Navega a página de colaboradores -->
            <button class="btn-icon w-7 h-7" title="Gestionar colaboradores"
                    @click="irColaboradores(n.nit)">
              <Users :size="12" />
            </button>
            <button class="btn-icon w-7 h-7  "
                    :class="{ 'hover:text-danger': n.status === 'Activo', 'hover:text-accent': n.status === 'Inactivo',
                      'hover:border-danger/30': n.status === 'Activo', 'hover:border-accent/30': n.status === 'Inactivo'
                    }"
                    :title="n.status === 'Activo' ? 'Desactivar' : 'Activar'" @click="editStatus(n)">

              <ThumbsUp :size="12" v-if="n.status === 'Inactivo'" />
              <ThumbsDown :size="12" v-else />
            </button>
          </div>
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
      </div>
    </CrudModal>

  </div>
</template>
