import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // forward API calls to your FastAPI backend
      '/search': 'http://localhost:8000',
      '/upload': 'http://localhost:8000',
      '/files':   'http://localhost:8000',
      '/feedback': 'http://localhost:8000'
    }
  }
})