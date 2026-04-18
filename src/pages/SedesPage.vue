<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, Pencil, Trash2, MapPin, ParkingCircle, ChevronRight, ArrowLeft } from 'lucide-vue-next'
import CrudModal from '@/components/CrudModal.vue'
import { sedesApi, negociosApi, catalogosApi } from '@/api/axios'
import { useToast } from 'vue-toastification'

const route  = useRoute()
const router = useRouter()
const toast  = useToast()

const nit     = route.params.nit
const negocio = ref(null)
const items   = ref([])
const paises  = ref([])
const deptos  = ref([])
const ciudades_exists = ref(true)
const ciudades = ref([])
const loading = ref(true)
const saving  = ref(false)
const modal   = ref({ open: false, mode: 'create', item: null })

const emptyForm = () => ({
  negocio: nit, nombre: '', direccion: '',
  country: '', state: '', city: '',
  // lat: '', lng: '',
})
const form = ref(emptyForm())

onMounted(async () => {
  const [negRes, sedesRes, paisRes] = await Promise.all([
    negociosApi.list({ nit }),
    sedesApi.list(nit),
    catalogosApi.paises(),
  ])
  const negs = negRes.data?.results ?? negRes.data ?? []
  negocio.value = negs.find(n => n.nit === nit) ?? null
  items.value   = sedesRes.data?.results ?? sedesRes.data ?? []
  paises.value  = paisRes.data?.results  ?? paisRes.data  ?? []
  loading.value = false
})

async function onPaisChange() {
  form.value.state = ''
  form.value.city = ''
  ciudades.value = []
  ciudades_exists.value = true
  if (!form.value.country) { deptos.value = []; return }
  const res = await catalogosApi.departamentos(form.value.country)
  deptos.value = res.data?.results ?? res.data ?? []
}
async function onDeptoChange() {
  form.value.city = ''
  if (!form.value.state) { ciudades.value = []; return }
  const res = await catalogosApi.ciudades(form.value.country, form.value.state)
  ciudades.value = res.data?.results ?? res.data ?? []
  ciudades_exists.value = ciudades.value.length > 0
}

function openCreate() { form.value = emptyForm(); modal.value = { open: true, mode: 'create', item: null } }
function openEdit(item) {
  form.value = {
    negocio: nit, nombre: item.nombre, direccion: item.direccion,
    country: item.country?.id ?? '', state: item.state?.id ?? '',
    city: item.city?.id ?? '', lat: item.lat ?? '', lng: item.lng ?? '',
  }
  modal.value = { open: true, mode: 'edit', item }
}
function closeModal() { modal.value.open = false }

async function handleSubmit() {
  saving.value = true
  try {
    if (modal.value.mode === 'create') {
      await sedesApi.create(nit, form.value)
      toast.success('Sede creada. Ahora puedes parametrizar sus puestos y tarifas.')
    } else {
      await sedesApi.update(nit, modal.value.item.uuid, form.value)
      toast.success('Sede actualizada')
    }
    closeModal()
    const res = await sedesApi.list(nit)
    items.value = res.data?.results ?? res.data ?? []
  } catch (err) {
    const msg = err.response?.data ? Object.values(err.response.data).flat().join(' · ') : 'Error al guardar'
    toast.error(msg)
  } finally { saving.value = false }
}

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

    <!-- Back + header -->
    <button class="flex items-center gap-1.5 text-xs text-t-muted hover:text-t-primary transition-colors mb-5" @click="router.back()">
      <ArrowLeft :size="13" /> Volver a negocios
    </button>

    <div class="flex justify-between items-start mb-7">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <ParkingCircle :size="16" class="text-accent" />
          <span class="text-xs text-t-muted font-medium">{{ negocio?.nombre ?? nit }}</span>
        </div>
        <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Sedes</h1>
        <p class="text-t-secondary text-sm mt-1">
          Cada sede es una ubicación física del parqueadero. Desde aquí parametrizas pisos, puestos y tarifas.
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

    <!-- Lista sedes -->
    <div v-else class="flex flex-col gap-3">
      <div v-for="s in items" :key="s.uuid"
           class="card-dark rounded-lg overflow-hidden hover:border-border-hover transition-all animate-fade-up">
        <div class="flex items-center gap-4 p-4">

          <!-- Icono sede -->
          <div class="w-10 h-10 rounded-sm bg-blue/10 border border-blue/20 flex items-center justify-center shrink-0">
            <MapPin :size="18" class="text-blue" />
          </div>

          <!-- Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-0.5">
              <span class="font-head font-bold text-t-primary text-sm">{{ s.nombre }}</span>
              <span :class="s.status === 'Activo' ? 'badge-green' : 'badge-red'">{{ s.status }}</span>
            </div>
            <div class="flex items-center gap-1 text-xs text-t-secondary">
              <MapPin :size="10" class="text-t-muted" />
              {{ s.direccion }} — {{ s.city?.name ?? '—' }}
            </div>
          </div>

          <!-- Stats rápidos -->
          <div class="hidden md:flex items-center gap-4 text-center">
            <div>
              <div class="text-[10px] text-t-muted uppercase tracking-wider">Puestos</div>
              <div class="font-head font-bold text-accent text-sm">{{ s.puestos_count ?? 0 }}</div>
            </div>
            <div>
              <div class="text-[10px] text-t-muted uppercase tracking-wider">Puntuación</div>
              <div class="font-head font-bold text-warn text-sm">{{ s.puntuacion ? Number(s.puntuacion).toFixed(1) : '—' }} ★</div>
            </div>
          </div>

          <!-- Acciones -->
          <div class="flex items-center gap-1.5 shrink-0">
            <button class="btn-icon w-8 h-8" title="Editar" @click="openEdit(s)"><Pencil :size="13" /></button>
            <button class="btn-icon w-8 h-8 hover:text-danger hover:border-danger/30" title="Eliminar" @click="handleDelete(s)"><Trash2 :size="13" /></button>
            <button class="btn-primary text-xs px-3 py-1.5 ml-1" @click="irPuestos(s.uuid)">
              Puestos <ChevronRight :size="12" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <CrudModal :open="modal.open"
      :title="modal.mode === 'create' ? 'Nueva sede' : 'Editar sede'"
      :loading="saving" size="lg" @close="closeModal" @submit="handleSubmit">
      <div>
        <label class="label-dark">NOMBRE DE LA SEDE</label>
        <input class="input-dark" v-model="form.nombre" placeholder="Ej: Sede Norte, Sede Centro" required />
      </div>
      <div>
        <label class="label-dark">DIRECCIÓN</label>
        <input class="input-dark" v-model="form.direccion" placeholder="Calle 26 # 13-20" required />
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
          <select class="input-dark" v-model="form.state" @change="onDeptoChange" required>
            <option value="">Selecciona</option>
            <option v-for="d in deptos" :key="d.id" :value="d.id">{{ d.name }}</option>
          </select>
        </div>
        <div >
          <label class="label-dark">CIUDAD</label>
          <select class="input-dark" v-model="form.city" :disabled="!ciudades_exists">
            <option value="">Selecciona</option>
            <option v-for="c in ciudades" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
      </div>
      <!-- <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="label-dark">LATITUD (GPS)</label>
          <input class="input-dark" type="number" step="any" v-model="form.lat" placeholder="4.7110" />
        </div>
        <div>
          <label class="label-dark">LONGITUD (GPS)</label>
          <input class="input-dark" type="number" step="any" v-model="form.lng" placeholder="-74.0721" />
        </div>
      </div> -->
    </CrudModal>

  </div>
</template>
