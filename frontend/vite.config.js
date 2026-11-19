import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The API base URL comes from VITE_API_URL (see .env.example).
export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
})
