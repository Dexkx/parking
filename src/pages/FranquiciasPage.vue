<script setup>
/**
 * FranquiciasPage.vue
 * CRUD de franquicias. El botón de colaboradores navega
 * a /franquicias/:uuid/colaboradores.
 */
import { ref, onMounted } from 'vue'
import { Plus, Pencil, ThumbsDown, ThumbsUp, Building2, Earth, Users } from 'lucide-vue-next'
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
  console.log(item)
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
    const msg = err.response?.data
      ? Object.values(err.response.data).flat().join(' · ')
      : 'Error al guardar'
    toast.error(msg)
  } finally { saving.value = false }
}

async function editStatus(item) {
  if (!confirm(`¿Desactivar la franquicia "${item.nombre}"? Sus negocios no podrán acceder a ella.`)) return
  try {
    const res = await franquiciasApi.editStatus(item.uuid, item.status === 'Activo' ? 'Inactivo' : 'Activo')
    toast.success(`Franquicia ${res.data?.status}`)
    const itemUpdate = items.value.find(n => n.nit === item.nit)
    itemUpdate.status = res.data?.status
    // await fetchAll()
  } catch { toast.error('No se pudo eliminar') }
}

// ── Navegación ──────────────────────────────────────────────
const irColaboradores = (uuid) => router.push({ name: 'colaboradores-franquicia', params: { uuid } })
const irNegocios      = (uuid) => router.push({ name: 'negocios', query: { franquicia: uuid } })
</script>

<template>
  <div class="p-6 max-w-screen-lg mx-auto">

    <!-- Header -->
    <div class="flex justify-between items-start mb-7">
      <div>
        <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Franquicias</h1>
        <p class="text-t-secondary text-sm mt-1">
          Empresas holding que agrupan múltiples negocios de parqueadero.
        </p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus :size="15" /> Nueva franquicia
      </button>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="flex flex-col gap-3">
      <div v-for="i in 4" :key="i" class="skeleton h-20" />
    </div>

    <!-- Vacío -->
    <div v-else-if="items.length === 0" class="card-dark rounded-lg py-16 text-center">
      <Earth :size="40" class="text-t-muted mx-auto mb-3" :stroke-width="1" />
      <p class="font-head font-bold text-t-primary mb-1">Sin franquicias</p>
      <p class="text-sm text-t-secondary">Crea tu primera franquicia para gestionar tus negocios.</p>
    </div>

    <!-- Tabla -->
    <div v-else class="card-dark rounded-lg overflow-hidden">

      <!-- Header -->
      <div class="grid grid-cols-[2fr_2fr_1fr_1fr_160px] bg-surface/50 border-b border-border">
        <div class="table-head-cell">Nombre</div>
        <div class="table-head-cell">Razón social</div>
        <div class="table-head-cell">NIT</div>
        <div class="table-head-cell">Estado</div>
        <div class="table-head-cell text-right pr-4">Acciones</div>
      </div>

      <div v-for="item in items" :key="item.uuid"
           class="grid grid-cols-[2fr_2fr_1fr_1fr_160px] border-b border-border last:border-0 hover:bg-card-hover transition-colors">

        <!-- Nombre -->
        <div class="flex items-center gap-2.5 px-4 py-3">
          <div class="w-8 h-8 rounded-sm bg-purple/10 border border-purple/20 flex items-center justify-center shrink-0">
            <Earth :size="14" class="text-purple" />
          </div>
          <span class="font-medium text-t-primary text-sm truncate">{{ item.nombre }}</span>
        </div>

        <!-- Razón social -->
        <div class="flex items-center px-4 py-3 text-t-secondary text-xs truncate">
          {{ item.razon_social ?? '—' }}
        </div>

        <!-- NIT -->
        <div class="flex items-center px-4 py-3 font-mono text-xs text-t-secondary">
          {{ item.nit ?? '—' }}
        </div>

        <!-- Estado -->
        <div class="flex items-center px-4 py-3">
          <span :class="item.status === 'Activo' ? 'badge-green' : 'badge-red'">{{ item.status }}</span>
        </div>

        <!-- Acciones -->
        <div class="flex items-center justify-end gap-1.5 pr-4 py-3">
          <!-- Ver negocios de la franquicia -->
          <button class="btn-icon w-7 h-7" title="Ver negocios" @click="irNegocios(item.uuid)">
            <Building2 :size="13" />
          </button>
          <!-- ← Navega a página de colaboradores -->
          <button class="btn-icon w-7 h-7" title="Gestionar colaboradores"
                  @click="irColaboradores(item.uuid)">
            <Users :size="13" />
          </button>
          <button class="btn-icon w-7 h-7" title="Editar" @click="openEdit(item)">
            <Pencil :size="13" />
          </button>
          <button class="btn-icon w-7 h-7  "
                    :class="{ 'hover:text-danger': item.status === 'Activo', 'hover:text-accent': item.status === 'Inactivo',
                      'hover:border-danger/30': item.status === 'Activo', 'hover:border-accent/30': item.status === 'Inactivo'
                    }"
                    :title="item.status === 'Activo' ? 'Desactivar' : 'Activar'" @click="editStatus(item)">

              <ThumbsUp :size="12" v-if="item.status === 'Inactivo'" />
              <ThumbsDown :size="12" v-else />
            </button>
        </div>
      </div>
    </div>

    <!-- Modal crear/editar -->
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
