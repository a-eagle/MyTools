import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    port: 8020,
    proxy: {
      // '/api': {
        // target: 'http://localhost:8010', // 后端地址
        // changeOrigin: true, // 开启跨域
        // secure: false,
        // ws: true,
        // rewrite: (path) => path.replace(/^\/api/, ''), // 重写路径,
        // pathRewrite: {'^/api': ''},  // 重写路径
        // },
    }
  }
})
