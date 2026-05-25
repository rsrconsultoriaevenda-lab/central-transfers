import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      strategy: 'injectManifest',
      srcDir: 'src',
      filename: 'sw.js',
      devOptions: {
        enabled: true,
        type: 'module',
      },
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'mask-icon.svg'],
      manifest: {
        name: 'Central Transfers - Painel',
        short_name: 'Transfers',
        description: 'Sistema de gestão de transfers e logística',
        theme_color: '#4c1d95',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      // Isso permite usar `@/` para importar de `src/`
      // Ex: import Login from '@/Login';
      // Ex: import SomeComponent from '@/components/SomeComponent';
      '@': path.resolve(__dirname, './src'), 
    },
  },
  test: {
    // Habilita o uso de APIs de teste globais (describe, it, expect)
    globals: true,
    // Define o ambiente de teste como JSDOM para simular um DOM de navegador
    environment: 'jsdom',
    // Arquivo de setup para configurar o ambiente de teste, como @testing-library/jest-dom
    setupFiles: './src/setupTests.ts', 
    // Transforma arquivos JSX/TSX
    transformMode: { web: [/\.(js|jsx|ts|tsx)$/] },
  },
});