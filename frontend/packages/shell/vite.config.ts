import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  plugins: [
    react(), 
    tailwindcss(),
    federation({
      name: 'shell',
      remotes: {
        'chat': 'http://localhost:5174/assets/remoteEntry.js',
        'upload': 'http://localhost:5175/assets/remoteEntry.js',
      },
      shared: ['react', 'react-dom', '@mfa/shared']
    })
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
  build: {
    target: 'esnext',
    minify: false,
    cssCodeSplit: false
  }
})
