<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, Trash2, ArrowLeft, DollarSign, Clock, ThumbsUp, ThumbsDown } from 'lucide-vue-next'
import CrudModal from '@/components/CrudModal.vue'
import { tarifasNegocioApi, catalogosApi } from '@/api/axios'
import { useToast } from 'vue-toastification'
import { negociosApi } from '../api/axios'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const nit = route.params.nit

const negocio = ref(null)
const items = ref([])
const tiposVeh = ref([])
const loading = ref(true)
const saving = ref(false)
const modal = ref({ open: false })

// Duración en horas y minutos → DurationField de Django espera HH:MM:SS
const durHoras = ref(1)
const durMins = ref(0)

const emptyForm = () => ({ negocio: nit, tipo_vehiculo: '', valor: '' })
const form = ref(emptyForm())

onMounted(async () => {
    const [negRes, tarifasRes, tvRes] = await Promise.all([
        negociosApi.list(),
        tarifasNegocioApi.list(nit),
        catalogosApi.tiposVehiculo(),
    ])
    const negocios = negRes.data?.results ?? negRes.data ?? []
    negocio.value = negocios.find(s => s.nit === nit) ?? null
    items.value = tarifasRes.data?.results ?? tarifasRes.data ?? []
    tiposVeh.value = tvRes.data?.results ?? tvRes.data ?? []
    loading.value = false
})

function openCreate() {
    form.value = emptyForm()
    durHoras.value = 1; durMins.value = 0
    modal.value.open = true
}
function closeModal() { modal.value.open = false }

// Convertir horas + minutos → HH:MM:SS
function buildTiempo() {
    const h = String(durHoras.value).padStart(2, '0')
    const m = String(durMins.value).padStart(2, '0')
    return `${h}:${m}:00`
}

async function handleSubmit() {
    saving.value = true
    try {
        await tarifasNegocioApi.create(nit, { ...form.value, tiempo: buildTiempo() })
        toast.success('Tarifa creada')
        closeModal()
        const res = await tarifasNegocioApi.list(nit)
        items.value = res.data?.results ?? res.data ?? []
    } catch (err) {
        toast.error(err.response?.data ? Object.values(err.response.data).flat().join(' · ') : 'Error al guardar')
    } finally { saving.value = false }
}

// ── Eliminar ───────────────────────────────────────
async function editStatus(item) {
    const accion = item.status === 'Activo' ? 'Desactivar' : 'Activar'
    if (!confirm(`¿${accion} la tarifa "${item.tipo_vehiculo?.name}"?`)) return

    try {
        const res = await tarifasNegocioApi.editStatus(nit, item.uuid, item.status === 'Activo' ? 'Inactivo' : 'Activo')
        toast.success(`Tarifa ${res.data?.status}`)

        const found = items.value.find(n => n.uuid === item.uuid)
        if (found) found.status = res.data?.status

    } catch { toast.error('No se pudo cambiar el estado') }
}

// Formatear duración legible
function fmtTiempo(d) {
    if (!d) return '—'
    const parts = d.split(':')
    const h = parseInt(parts[0])
    const m = parseInt(parts[1])
    if (h && m) return `${h}h ${m}min`
    if (h) return `${h} hora${h > 1 ? 's' : ''}`
    return `${m} min`
}

const alcance = (t) => {
    if (t.numero) return `Puesto ${t.piso}·#${t.numero}`
    if (t.piso) return `Piso ${t.piso}`
    return 'Toda el negocio'
}
</script>

<template>
    <div class="p-6 max-w-screen-lg mx-auto">

        <!-- Back -->
        <button class="flex items-center gap-1.5 text-xs text-t-muted hover:text-t-primary mb-5" @click="router.back()">
            <ArrowLeft :size="13" /> Volver a negocios
        </button>

        <!-- Header -->
        <div class="flex justify-between items-start mb-7">
            <div>
                <div class="flex items-center gap-2 mb-1">
                    <DollarSign :size="14" class="text-accent" />
                    <span class="text-xs text-t-muted">{{ negocio?.nombre ?? nit }}</span>
                </div>
                <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">Tarifas</h1>
                <p class="text-t-secondary text-sm mt-1">
                    Aplica a todo el negocio. <br>
                    Estas tarifas se ommiten si especificas por sede, piso, o puesto.
                </p>
            </div>
            <button class="btn-primary" @click="openCreate">
                <Plus :size="15" /> Nueva tarifa
            </button>
        </div>

        <!-- Skeleton -->
        <div v-if="loading" class="flex flex-col gap-2">
            <div v-for="i in 4" :key="i" class="skeleton h-14" />
        </div>

        <!-- Vacío -->
        <div v-else-if="items.length === 0" class="card-dark rounded-lg py-14 text-center">
            <DollarSign :size="36" class="text-t-muted mx-auto mb-3" :stroke-width="1" />
            <p class="font-head font-bold text-t-primary mb-1">Sin tarifas</p>
            <p class="text-sm text-t-secondary">Crea al menos una tarifa general para este negocio.</p>
        </div>

        <!-- Tabla de tarifas → Grid de tarjetas -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="t in items" :key="`${t.tipo_vehiculo_id}-${t.tiempo}`"
                class="card-dark rounded-lg overflow-hidden hover:border-border-hover transition-all animate-fade-up"
                :class="{ '!opacity-60': t.status !== 'Activo' }">

                <!-- Top -->
                <div class="flex items-start justify-between p-4 pb-3">
                    <div class="flex items-start gap-3 flex-1 min-w-0">
                        <div
                            class="w-9 h-9 rounded-sm bg-accent/10 border border-accent/20 flex items-center justify-center shrink-0">
                            <DollarSign :size="16" class="text-accent" />
                        </div>
                        <div class="min-w-0">
                            <div class="font-head font-bold text-t-primary text-sm leading-tight truncate">
                                {{ t.tipo_vehiculo?.name ?? t.tipo_vehiculo }}
                            </div>
                            <div class="font-mono text-[11px] text-t-muted mt-0.5">ID: {{ t.uuid }}</div>
                        </div>
                    </div>
                    <span :class="[
                        !t.piso && !t.numero ? 'badge-green' :
                            !t.numero ? 'badge-blue' : 'badge-purple'
                    ]" class="shrink-0 ml-2">
                        {{ alcance(t) }}
                    </span>
                </div>

                <!-- Stats -->
                <div class="grid grid-cols-2 gap-px bg-border mx-4 rounded-sm overflow-hidden mb-3">
                    <div class="bg-input px-3 py-2 text-center">
                        <div class="text-[10px] text-t-muted uppercase tracking-wider mb-0.5">Duración</div>
                        <div class="font-head font-bold text-accent text-sm flex items-center justify-center gap-1">
                            <Clock :size="12" /> {{ fmtTiempo(t.tiempo) }}
                        </div>
                    </div>
                    <div class="bg-input px-3 py-2 text-center">
                        <div class="text-[10px] text-t-muted uppercase tracking-wider mb-0.5">Valor (COP)</div>
                        <div class="font-head font-bold text-t-primary text-sm">
                            ${{ Number(t.valor).toLocaleString('es-CO') }}
                        </div>
                    </div>
                </div>

                <!-- Footer acciones -->
                <div class="flex items-center justify-between px-4 py-3 border-t border-border bg-surface/30">
                    <div class="flex gap-1">
                        <button class="btn-icon w-7 h-7" :class="{
                            'hover:text-danger hover:border-danger/30': t.status === 'Activo',
                            'hover:text-accent hover:border-accent/30': t.status === 'Inactivo',
                        }" :title="t.status === 'Activo' ? 'Desactivar' : 'Activar'" @click="editStatus(t)">
                            <ThumbsUp :size="12" v-if="t.status === 'Inactivo'" />
                            <ThumbsDown :size="12" v-else />
                        </button>
                    </div>
                    <div class="text-[10px] text-t-muted font-mono uppercase">{{ t.status }}</div>
                </div>
            </div>
        </div>

        <!-- Modal nueva tarifa -->
        <CrudModal :open="modal.open" title="Nueva tarifa" :loading="saving" size="lg" submit-label="Crear tarifa"
            @close="closeModal" @submit="handleSubmit">

            <div>
                <label class="label-dark">TIPO DE VEHÍCULO</label>
                <select class="input-dark" v-model="form.tipo_vehiculo" required>
                    <option value="">Selecciona</option>
                    <option v-for="tv in tiposVeh" :key="tv.id" :value="tv.id">{{ tv.name }}</option>
                </select>
            </div>

            <!-- Duración -->
            <div>
                <label class="label-dark">DURACIÓN (FRACCIÓN DE TIEMPO)</label>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="text-xs text-t-muted mb-1 block">Horas</label>
                        <input class="input-dark" type="number" min="0" max="23" v-model="durHoras" />
                    </div>
                    <div>
                        <label class="text-xs text-t-muted mb-1 block">Minutos</label>
                        <input class="input-dark" type="number" min="0" max="59" step="5" v-model="durMins" />
                    </div>
                </div>
                <div class="text-xs text-t-muted mt-1">
                    Fracción configurada: <span class="text-accent font-semibold">{{ buildTiempo() }}</span>
                </div>
            </div>

            <!-- Valor -->
            <div>
                <label class="label-dark">VALOR EN COP</label>
                <div class="relative">
                    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-t-muted text-sm">$</span>
                    <input class="input-dark pl-7" type="number" min="0" v-model="form.valor" placeholder="5000"
                        required />
                </div>
            </div>

            <p class="text-xs text-t-muted mb-3">
                Recuerda que la tarifa se aplica a todo el negocio.
            </p>
        </CrudModal>

    </div>
</template>
