/**
 * Axios 实例封装
 * - baseURL 统一指向 /api（由 Vite 代理转发到后端）
 * - 请求拦截器：自动在 Authorization 头携带 JWT 令牌
 * - 响应拦截器：遇到 401 时自动清除登录状态并跳转登录页
 */
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const http = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// 请求拦截器：注入 Bearer Token
http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// 响应拦截器：401 → 退出登录并跳转
http.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout()
      router.push('/login')
    }
    return Promise.reject(err)
  }
)

export default http
