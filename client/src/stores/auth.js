/**
 * Pinia 认证状态库
 * 管理登录状态、JWT 令牌以及用户基本信息。
 * 令牌和有效字段持久化到 localStorage，刷新后自动恢复。
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  // 从 localStorage 恢复登录状态
  const token = ref(localStorage.getItem('token') || '')
  const role = ref(localStorage.getItem('role') || '')
  const userId = ref(Number(localStorage.getItem('userId')) || null)
  const employeeId = ref(Number(localStorage.getItem('employeeId')) || null)
  const name = ref(localStorage.getItem('userName') || '')

  const isLoggedIn = computed(() => !!token.value)
  const isManager = computed(() => role.value === 'manager' || role.value === 'admin')
  const isAdmin = computed(() => role.value === 'admin')

  /** 调用登录接口，将返回的 token 及用户信息写入 store 和 localStorage */
  async function login(username, password) {
    const res = await authApi.login({ username, password })
    const data = res.data
    token.value = data.access_token
    role.value = data.role
    userId.value = data.user_id
    employeeId.value = data.employee_id
    name.value = data.name
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('role', data.role)
    localStorage.setItem('userId', data.user_id)
    localStorage.setItem('employeeId', data.employee_id)
    localStorage.setItem('userName', data.name)
  }

  /** 清除 store 和 localStorage 中的登录状态 */
  function logout() {
    token.value = ''
    role.value = ''
    userId.value = null
    employeeId.value = null
    name.value = ''
    localStorage.clear()
  }

  return { token, role, userId, employeeId, name, isLoggedIn, isManager, isAdmin, login, logout }
})
