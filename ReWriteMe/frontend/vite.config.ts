import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API requests to the backend running on localhost:8000
      '/rewrite': 'http://localhost:8000',
      '/emotion': 'http://localhost:8000',
      '/history': 'http://localhost:8000'
    }
  }
});