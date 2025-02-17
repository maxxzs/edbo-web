import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  envDir: '../', // 指定环境文件查找目录
  envPrefix: 'VITE_', // 只暴露VITE_开头的环境变量
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  define: {
    'process.env': process.env,
    '__VUE_PROD_HYDRATION_MISMATCH_DETAILS__': false
  }
})
