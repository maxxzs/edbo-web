import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'

// 全局样式
import './assets/styles/global.css'

const app = createApp(App)

// 配置axios基础路径
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://8.139.254.79:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

app.config.globalProperties.$api = apiClient

// 配置API基础地址
import axios from 'axios'
// 生产环境配置
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://8.139.254.79:8000' // 请替换为实际云服务器IP
axios.defaults.timeout = 30000

// 添加响应拦截器
axios.interceptors.response.use(response => {
  return response
}, error => {
  if (error.response) {
    console.error('API Error:', {
      status: error.response.status,
      data: error.response.data
    })
  }
  return Promise.reject(error)
})

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.mount('#app')
