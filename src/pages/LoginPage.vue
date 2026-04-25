<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ParkingCircle, Eye, EyeOff, Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const auth     = useAuthStore()
const router   = useRouter()
const toast    = useToast()
const loading  = ref(false)
const showPass = ref(false)
const form     = ref({ numero_id: '', password: '' })

async function handleLogin() {
  loading.value = true
  try {
    await auth.login(form.value.numero_id, form.value.password)
    toast.success('¡Bienvenido al dashboard!')
    router.push('/')
  } catch (error) {
    console.log(error)
    const data = error.response.data
    let text_error = data.detail

    if (!text_error)
      text_error = data.non_field_errors.join(' | ')

    toast.error(text_error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-base flex items-center justify-center p-4">
    <!-- Fondo con gradiente sutil -->
    <div class="absolute inset-0 pointer-events-none"
         style="background: radial-gradient(ellipse 80% 50% at 50% 0%, rgba(0,229,176,0.06), transparent)" />

    <div class="w-full max-w-sm relative">

      <!-- Logo -->
      <div class="flex flex-col items-center mb-8">
        <div class="w-14 h-14 rounded-xl bg-accent/10 border border-accent/20 flex items-center justify-center mb-4 shadow-glow">
          <ParkingCircle :size="28" class="text-accent" :stroke-width="2" />
        </div>
        <h1 class="font-head font-extrabold text-2xl text-t-primary tracking-tight">
          <span class="text-accent">Park</span>App Dashboard
        </h1>
        <p class="text-t-secondary text-sm mt-1">Panel de administración</p>
      </div>

      <!-- Card -->
      <div class="card-dark rounded-xl p-7">
        <form @submit.prevent="handleLogin" class="flex flex-col gap-5">

          <div>
            <label class="label-dark">N° IDENTIFICACIÓN</label>
            <input class="input-dark" v-model="form.numero_id"
                   placeholder="Ej: 1234567890" required autofocus />
          </div>

          <div>
            <label class="label-dark">CONTRASEÑA</label>
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
            <span v-else>Ingresar al dashboard →</span>
          </button>
        </form>
      </div>

      <p class="text-center text-xs text-t-muted mt-5">
        Solo para administradores y dueños de negocios registrados.
      </p>
    </div>
  </div>
</template>
