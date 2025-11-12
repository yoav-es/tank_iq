// ui/vite.config.ts

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  // CRITICAL: Setup the proxy to forward API requests to the FastAPI backend
  server: {
    proxy: {
      // Any request starting with /entries/ or /stats/ will be redirected to the backend.
      '/entries/': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false, // For local development
      },
      '/stats/': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false, 
      },
    },
    // Ensure the frontend runs on a different port than the backend (e.g., 5173 vs 8000)
    port: 5173,
    strictPort: true,
  },
});