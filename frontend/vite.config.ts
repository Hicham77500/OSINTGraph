import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': 'http://localhost:8000',
      '/graph': 'http://localhost:8000',
      '/transforms': 'http://localhost:8000',
      '/workspaces': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
      '/socket.io': {
        target: 'http://localhost:8000',
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  base: process.env.VITE_BASE_PATH || './',
})
