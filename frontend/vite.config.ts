import path from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': path.resolve(import.meta.dirname, './src') },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: false,
  },
  server: {
    // localhost only: don't expose the app + data to the venue Wi-Fi.
    // To demo on another device on purpose: VITE_HOST=0.0.0.0 npm run dev
    host: process.env.VITE_HOST ?? 'localhost',
    port: 5173,
    // Proxy API calls to FastAPI in dev so the frontend can use relative /api URLs
    proxy: {
      '/api': {
        target: process.env.VITE_PROXY_TARGET ?? 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
