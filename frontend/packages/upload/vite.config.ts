import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  plugins: [
    react(), 
    tailwindcss(),
    federation({
      name: 'upload',
      filename: 'remoteEntry.js',
      exposes: {
        './UploadPage': './src/components/UploadPage.tsx',
      },
      shared: ['react', 'react-dom', '@mfa/shared']
    })
  ],
  server: {
    port: 5175,
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
