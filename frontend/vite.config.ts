import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Port 5173 must match BACKEND_CORS_ORIGINS in the backend .env
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, strictPort: true },
})
