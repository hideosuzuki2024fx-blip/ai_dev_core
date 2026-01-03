import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API requests to the backend running on localhost:8000
      '/rewrite': 'http://127.0.0.1:8000',
      '/emotion': 'http://127.0.0.1:8000',
      '/history': 'http://127.0.0.1:8000'
    }
  }
});
