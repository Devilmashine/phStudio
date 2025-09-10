import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { nodePolyfills } from 'vite-plugin-node-polyfills';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
  plugins: [
    react(),
    nodePolyfills({
      globals: {
        Buffer: true,
        global: true,
        process: true,
      },
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src'),
    },
  },
  root: '.', // Указываем, что корень проекта для Vite - это текущая директория
  build: {
    outDir: 'dist', // Выходная директория
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html'), // Путь относительно корня
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8888',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});