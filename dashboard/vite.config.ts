/// <reference types="vitest/config" />
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/setupTests.ts',
  },
  server: {
    port: 3000,
    host: true,
    // proxy the API so dev is same-origin as the data service - the httpOnly
    // JWT cookie and CSRF then work without cross-origin cookie handling
    proxy: {
      '/api': {
        target: process.env.VITE_DATA_API_HOST || 'http://localhost:5003',
        changeOrigin: true,
      },
    },
  },
})
