<script setup>
/**
 * LoginModal.vue
 * Modal con dos tabs: Ingresar y Registrarse.
 *
 * Props:   open (Boolean)
 * Emits:   close
 *
 * Usa el store de auth para login.
 * Usa authApi.register para el registro.
 */
import { ref, watch } from 'vue'
import { X, Eye, EyeOff, Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/axios'
import { useToast } from 'vue-toastification'

const props = defineProps({ open: Boolean })
const emit  = defineEmits(['close'])

const auth  = useAuthStore()
const toast = useToast()

// ── Estado local ──────────────────────────
const tab      = ref('login')   // 'login' | 'register'
const showPass = ref(false)
const loading  = ref(false)

// Formulario unificado: se usan los campos según el tab
const form = ref({
  numero_id:        '',
  password:         '',
  confirm_password: '',
  nombre:           '',
  tipo_id:          'CC',
})

// Resetear al abrir el modal
watch(() => props.open, (val) => {
  if (val) { tab.value = 'login'; Object.keys(form.value).forEach(k => { form.value[k] = k === 'tipo_id' ? 'CC' : '' }) }
})

// ── Login ─────────────────────────────────
async function handleLogin() {
  loading.value = true
  try {
    await auth.login(form.value.numero_id, form.value.password)
    toast.success('¡Bienvenido de nuevo!')
    emit('close')
  } catch {
    toast.error('Número de identificación o contraseña incorrectos')
  } finally { loading.value = false }
}

// ── Registro ──────────────────────────────
async function handleRegister() {
  if (form.value.password !== form.value.confirm_password) {
    toast.warning('Las contraseñas no coinciden'); return
  }
  loading.value = true
  try {
    await authApi.register({
      numero_id:        form.value.numero_id,
      password:         form.value.password,
      confirm_password: form.value.confirm_password,
      nombre:           form.value.nombre,
      tipo_id:          form.value.tipo_id,
    })
    toast.success('Cuenta creada. Ahora puedes ingresar.')
    tab.value = 'login'
  } catch (err) {
    const data = err.response?.data
    const msg  = data ? Object.values(data).flat().join(' · ') : 'Error al registrarse'
    toast.error(msg)
  } finally { loading.value = false }
}
</script>

<template>
  <!-- Overlay -->
  <Transition name="modal">
    <div v-if="open"
         class="fixed inset-0 z-[9999] flex items-center justify-center p-4"
         style="background:rgba(0,0,0,0.75);backdrop-filter:blur(8px)"
         @click.self="$emit('close')">

      <!-- Panel -->
      <div class="w-full max-w-md bg-card border border-border rounded-xl overflow-hidden shadow-[0_24px_80px_rgba(0,0,0,0.6)]">

        <!-- Encabezado -->
        <div class="flex justify-between items-start p-6 pb-0">
          <div>
            <h2 class="font-head font-extrabold text-2xl tracking-tight">
              {{ tab === 'login' ? 'Bienvenido' : 'Crear cuenta' }}
            </h2>
            <p class="text-t-secondary text-sm mt-1">
              {{ tab === 'login' ? 'Ingresa para reservar tu espacio' : 'Regístrate y comienza a reservar' }}
            </p>
          </div>
          <button class="p-1.5 rounded-sm bg-input border border-border text-t-secondary hover:text-t-primary transition-colors"
                  @click="$emit('close')">
            <X :size="15" />
          </button>
        </div>

        <!-- Tabs -->
        <div class="flex gap-1 mx-6 mt-5 p-1 bg-input rounded-sm">
          <button :class="['flex-1 py-2 rounded text-xs font-semibold transition-all',
                           tab === 'login' ? 'bg-card text-t-primary shadow' : 'text-t-muted']"
                  @click="tab = 'login'">Ingresar</button>
          <button :class="['flex-1 py-2 rounded text-xs font-semibold transition-all',
                           tab === 'register' ? 'bg-card text-t-primary shadow' : 'text-t-muted']"
                  @click="tab = 'register'">Registrarse</button>
        </div>

        <!-- Cuerpo -->
        <div class="p-6">

          <!-- ─── Formulario Login ─── -->
          <form v-if="tab === 'login'" @submit.prevent="handleLogin" class="flex flex-col gap-4">
            <div>
              <label class="label-dark block mb-1.5">N° IDENTIFICACIÓN</label>
              <input class="input-dark" v-model="form.numero_id" placeholder="Ej: 1234567890" required />
            </div>
            <div>
              <label class="label-dark block mb-1.5">CONTRASEÑA</label>
              <div class="relative">
                <input class="input-dark pr-10"
                       :type="showPass ? 'text' : 'password'"
                       v-model="form.password" required />
                <button type="button"
                        class="absolute right-3 top-1/2 -translate-y-1/2 text-t-muted hover:text-t-secondary transition-colors"
                        @click="showPass = !showPass">
                  <EyeOff v-if="showPass" :size="15" />
                  <Eye v-else :size="15" />
                </button>
              </div>
            </div>
            <button type="submit" class="btn-primary w-full justify-center py-3 mt-1" :disabled="loading">
              <Loader2 v-if="loading" :size="15" class="animate-spin" />
              <span v-else>Ingresar →</span>
            </button>
          </form>

          <!-- ─── Formulario Registro ─── -->
          <form v-else @submit.prevent="handleRegister" class="flex flex-col gap-3.5">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="label-dark block mb-1.5">TIPO ID</label>
                <select class="input-dark" v-model="form.tipo_id">
                  <option value="CC">Cédula (CC)</option>
                  <option value="TI">T. Identidad (TI)</option>
                  <option value="CE">C. Extranjería</option>
                  <option value="PPT">PPT</option>
                </select>
              </div>
              <div>
                <label class="label-dark block mb-1.5">N° IDENTIFICACIÓN</label>
                <input class="input-dark" v-model="form.numero_id" placeholder="1234567890" required />
              </div>
            </div>
            <div>
              <label class="label-dark block mb-1.5">NOMBRE COMPLETO</label>
              <input class="input-dark" v-model="form.nombre" placeholder="Tu nombre completo" required />
            </div>
            <div>
              <label class="label-dark block mb-1.5">CONTRASEÑA</label>
              <div class="relative">
                <input class="input-dark pr-10"
                       :type="showPass ? 'text' : 'password'"
                       v-model="form.password" required />
                <button type="button"
                        class="absolute right-3 top-1/2 -translate-y-1/2 text-t-muted hover:text-t-secondary"
                        @click="showPass = !showPass">
                  <EyeOff v-if="showPass" :size="15" />
                  <Eye v-else :size="15" />
                </button>
              </div>
            </div>
            <div>
              <label class="label-dark block mb-1.5">CONFIRMAR CONTRASEÑA</label>
              <input class="input-dark" type="password" v-model="form.confirm_password" required />
            </div>
            <button type="submit" class="btn-primary w-full justify-center py-3 mt-1" :disabled="loading">
              <Loader2 v-if="loading" :size="15" class="animate-spin" />
              <span v-else>Crear cuenta →</span>
            </button>
          </form>

        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity .2s, transform .2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95) translateY(12px); }
</style>
