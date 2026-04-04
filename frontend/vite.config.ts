import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

const __dirname = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(__dirname, '..')

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, repoRoot, '')
  const frontendPort = Number(env.FRONTEND_PORT ?? '5173')
  const backendOrigin = env.BACKEND_ORIGIN ?? env.VITE_API_BASE_URL ?? 'http://localhost:8000'

  return {
    plugins: [react()],
    server: {
      port: frontendPort,
      proxy: {
        '/api': {
          target: backendOrigin,
          changeOrigin: true,
        },
        '/data': {
          target: backendOrigin,
          changeOrigin: true,
        }
      }
    }
  }
})
