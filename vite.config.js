import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  return {
    plugins: [vue()],
    resolve: {
      alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) }
    },
    server: {
      port: 5174,
      proxy: {
        '/api': { target: env.VITE_BACKEND_URL, changeOrigin: true },
        '/nomination-api': {
          target: env.VITE_NOMINATION_API,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/nomination-api/, '')
        }
      }
    }
  }
})
