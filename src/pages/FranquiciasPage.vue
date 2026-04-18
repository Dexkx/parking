<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Pencil, Trash2, Building2, ChevronRight } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import CrudModal from '@/components/CrudModal.vue'
import { franquiciasApi } from '@/api/axios'
import { useToast } from 'vue-toastification'

const router = useRouter()
const toast  = useToast()

const items   = ref([])
const loading = ref(true)
const saving  = ref(false)
const modal   = ref({ open: false, mode: 'create', item: null })

const emptyForm = () => ({ nit: '', numero_verificacion: '', razon_social: '', nombre: '' })
const form = ref(emptyForm())

onMounted(fetch)

async function fetch() {
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
  form.value = { ...item }
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
    await fetch()
  } catch (err) {
    const msg = err.response?.data ? Object.values(err.response.data).flat().join(' · ') : 'Error al guardar'
    toast.error(msg)
  } finally { saving.value = false }
}

async function handleDelete(item) {
  if (!confirm(`¿Eliminar la franquicia "${item.nombre}"?`)) return
  try {
    await franquiciasApi.remove(item.uuid)
    toast.success('Franquicia eliminada')
    await fetch()
  } catch { toast.error('No se pudo eliminar') }
}
</script>

<template>
  <div class="p-6 max-w-screen-lg mx-auto">

    <!-- Header -->
    <div class="flex justify-between items-start mb-7">
      <div>
        <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Franquicias</h1>
        <p class="text-t-secondary text-sm mt-1">Empresas holding que agrupan múltiples negocios de parqueadero.</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus :size="15" /> Nueva franquicia
      </button>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="flex flex-col gap-3">
      <div v-for="i in 4" :key="i" class="skeleton h-20" />
    </div>

    <!-- Lista -->
    <div v-else-if="items.length === 0" class="card-dark rounded-lg py-16 text-center">
      <Building2 :size="40" class="text-t-muted mx-auto mb-3" :stroke-width="1" />
      <p class="font-head font-bold text-t-primary mb-1">Sin franquicias</p>
      <p class="text-sm text-t-secondary">Crea tu primera franquicia para comenzar a gestionar tus negocios.</p>
    </div>

    <div v-else class="card-dark rounded-lg overflow-hidden">
      <!-- Cols header -->
      <div class="table-row grid-cols-[2fr_2fr_1fr_120px] bg-surface/50">
        <div class="table-head-cell">Nombre</div>
        <div class="table-head-cell">Razón social</div>
        <div class="table-head-cell">NIT</div>
        <div class="table-head-cell justify-end">Acciones</div>
      </div>

      <div v-for="item in items" :key="item.uuid" class="table-row grid-cols-[2fr_2fr_1fr_120px]">
        <div class="table-cell">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-sm bg-purple/10 border border-purple/20 flex items-center justify-center shrink-0">
              <Building2 :size="14" class="text-purple" />
            </div>
            <div>
              <div class="font-medium text-t-primary text-sm">{{ item.nombre }}</div>
              <span :class="item.status === 'Activo' ? 'badge-green' : 'badge-red'" class="mt-0.5">
                {{ item.status }}
              </span>
            </div>
          </div>
        </div>
        <div class="table-cell text-t-secondary text-xs">{{ item.razon_social ?? '—' }}</div>
        <div class="table-cell font-mono text-xs text-t-secondary">{{ item.nit ?? '—' }}</div>
        <div class="table-cell justify-end gap-1">
          <button class="btn-icon w-7 h-7" title="Ver negocios"
                  @click="router.push({ name: 'negocios', query: { franquicia: item.uuid } })">
            <ChevronRight :size="13" />
          </button>
          <button class="btn-icon w-7 h-7" title="Editar" @click="openEdit(item)">
            <Pencil :size="13" />
          </button>
          <button class="btn-icon w-7 h-7 hover:text-danger hover:border-danger/30" title="Eliminar" @click="handleDelete(item)">
            <Trash2 :size="13" />
          </button>
        </div>
      </div>
    </div>

    <!-- Modal create/edit -->
    <CrudModal :open="modal.open" :title="modal.mode === 'create' ? 'Nueva franquicia' : 'Editar franquicia'"
               :loading="saving" @close="closeModal" @submit="handleSubmit">
      <div>
        <label class="label-dark">NOMBRE VISIBLE EN LA APP</label>
        <input class="input-dark" v-model="form.nombre" placeholder="Ej: Parkings del Norte S.A.S" required />
      </div>
      <div>
        <label class="label-dark">RAZÓN SOCIAL</label>
        <input class="input-dark" v-model="form.razon_social" placeholder="Razón social completa" />
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
