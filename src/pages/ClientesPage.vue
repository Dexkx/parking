<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus, Trash2, Users, Search, ThumbsDown, ThumbsUp } from 'lucide-vue-next'
import CrudModal from '@/components/CrudModal.vue'
import { clientesApi, negociosApi } from '@/api/axios'
import { useToast } from 'vue-toastification'

const toast = useToast()
const negocios = ref([])
const nitActivo = ref('')
const clientes = ref([])
const loading = ref(true)
const saving = ref(false)
const query = ref('')
const modal = ref({ open: false })
const form = ref({ usuario: '' })

onMounted(async () => {
  const res = await negociosApi.list()
  negocios.value = res.data?.results ?? res.data ?? []
  if (negocios.value.length > 0) {
    nitActivo.value = negocios.value[0].nit
    await cargarClientes()
  }
  loading.value = false
})

async function cargarClientes() {
  if (!nitActivo.value) return
  loading.value = true
  try {
    const res = await clientesApi.list(nitActivo.value)
    clientes.value = res.data?.results ?? res.data ?? []
  } finally { loading.value = false }
}

const lista = computed(() => {
  if (!query.value) return clientes.value
  const q = query.value.toLowerCase()
  return clientes.value.filter(c =>
    c.usuario?.nombre?.toLowerCase().includes(q) ||
    c.usuario?.numero_id?.includes(q)
  )
})

function openCreate() { form.value = { usuario: '' }; modal.value.open = true }
function closeModal() { modal.value.open = false }

async function handleSubmit() {
  saving.value = true
  try {
    await clientesApi.create(nitActivo.value, { negocio: nitActivo.value, usuario: form.value.usuario })
    toast.success('Cliente registrado con membresía mensual')
    closeModal()
    await cargarClientes()
  } catch (err) {
    toast.error(err.response?.data ? Object.values(err.response.data).flat().join(' · ') : 'Error')
  } finally { saving.value = false }
}

async function editStatus(item) {
  const accion = item.status.value === 'Activo' ? 'Desactivar' : 'Activar'
  if (!confirm(`¿${accion} el cliente "${item.usuario?.nombre}"?`)) return
  try {
    const res = await clientesApi.editStatus(nitActivo.value, item.usuario.numero_id, item.status.value === 'Activo' ? 'Inactivo' : 'Activo')
    toast.success(`Cliente ${res.data?.status.value}`)
    const found = lista.value.find(n => n.usuario.numero_id === item.usuario.numero_id)
    if (found) found.status.value = res.data?.status.value
  } catch { toast.error('No se pudo cambiar el estado') }
}

async function deleteClient(item) {
  if (!confirm(`¿Eliminar el cliente "${item.usuario?.nombre}"?`)) return
  
  try {
    await clientesApi.delete(nitActivo.value, item.usuario.numero_id)
    toast.success('Cliente eliminado correctamente')
    await cargarClientes()
  } catch { toast.error('No se pudo eliminar el cliente') }
}
</script>

<template>
  <div class="p-6 max-w-screen-lg mx-auto">
    <div class="flex justify-between items-start mb-7">
      <div>
        <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Clientes</h1>
        <p class="text-t-secondary text-sm mt-1">Clientes con membresía mensual. Pueden reservar y pagar
          anticipadamente.</p>
      </div>
      <button class="btn-primary" @click="openCreate" :disabled="!nitActivo">
        <Plus :size="15" /> Agregar cliente
      </button>
    </div>

    <!-- Selector de negocio + buscador -->
    <div class="flex gap-3 mb-5">
      <select class="input-dark w-64" v-model="nitActivo" @change="cargarClientes">
        <option v-for="n in negocios" :key="n.nit" :value="n.nit">{{ n.nombre }}</option>
      </select>
      <div class="flex items-center gap-2 flex-1 bg-input border border-border rounded-sm px-3 py-2">
        <Search :size="13" class="text-t-muted shrink-0" />
        <input v-model="query"
          class="flex-1 bg-transparent border-none outline-none text-sm text-t-primary placeholder:text-t-muted"
          placeholder="Buscar por nombre o número de ID..." />
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="flex flex-col gap-2">
      <div v-for="i in 5" :key="i" class="skeleton h-14" />
    </div>

    <!-- Vacío -->
    <div v-else-if="lista.length === 0" class="card-dark rounded-lg py-14 text-center">
      <Users :size="36" class="text-t-muted mx-auto mb-3" :stroke-width="1" />
      <p class="font-head font-bold text-t-primary mb-1">Sin clientes registrados</p>
      <p class="text-sm text-t-secondary">Agrega clientes para gestionar membresías mensuales.</p>
    </div>

    <!-- Tabla -->
    <div v-else class="card-dark rounded-lg overflow-hidden">
      <table class="w-full border-collapse">
        <thead>
          <tr class="bg-surface/50 border-b border-border">
            <th class="table-head-cell">Nombre</th>
            <th class="table-head-cell">N° Identificación</th>
            <th class="table-head-cell">Estado</th>
            <th class="table-head-cell">Acción</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in lista" :key="c.usuario?.numero_id ?? c.usuario"
            class="border-b border-border last:border-0 hover:bg-surface/30 transition-all duration-300 group">
            <td class="table-cell">
              <div class="flex flex-row gap-2.5 items-center">
                <div
                  class="w-7 h-7 rounded-full bg-blue/10 border border-blue/20 flex items-center justify-center text-blue text-xs font-bold font-head shrink-0">
                  {{ (c.usuario?.nombre ?? '?').charAt(0).toUpperCase() }}
                </div>
                <span class="font-medium text-t-primary truncate">{{ c.usuario?.nombre ?? '—' }}</span>
              </div>
            </td>
            <td class="table-cell font-mono text-xs text-t-secondary">{{ c.usuario?.numero_id ?? '—' }}</td>
            <td class="table-cell">
              <span :class="c.status.value === 'Activo' ? 'badge-green' : 'badge-red'">{{ c.status.value }}</span>
            </td>
            <td class="table-cell justify-end">
              <div class="flex flex-row flex-wrap gap-2">
                <button class="btn-icon w-7 h-7"
                  :class="{ 'hover:text-danger hover:border-danger/30': c.status.value === 'Activo',
                    'hover:text-accent hover:border-accent/30': c.status.value === 'Inactivo'}"
                  :title="`${c.status.value === 'Activo' ? 'Desactivar' : 'Activar'} membresía`" @click="editStatus(c)">
                  <ThumbsDown v-if="c.status.value === 'Activo'" :size="13" />
                  <ThumbsUp v-else :size="13" />
                </button>
                <button class="btn-icon w-7 h-7 hover:text-danger hover:border-danger/30"
                  title="Eliminar cliente" @click="deleteClient(c)">
                  <Trash2 size="13"/>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal agregar cliente -->
    <CrudModal :open="modal.open" title="Agregar cliente" :loading="saving" submit-label="Registrar membresía"
      @close="closeModal" @submit="handleSubmit">
      <div class="bg-input/50 rounded-sm p-3 text-xs text-t-muted border border-border mb-1">
        El cliente debe tener cuenta en ParkApp. Ingresa su número de identificación.
      </div>
      <div>
        <label class="label-dark">N° IDENTIFICACIÓN DEL CLIENTE</label>
        <input class="input-dark" v-model="form.usuario" placeholder="Ej: 1234567890" required />
      </div>
    </CrudModal>
  </div>
</template>
