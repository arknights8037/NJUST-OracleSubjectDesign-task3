<template>
  <div class="min-h-screen bg-[#1c1c1e] flex items-center justify-center px-4">
    <!-- 背景纹理层 -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute inset-0 opacity-[0.03]"
           style="background-image:repeating-linear-gradient(0deg,rgba(255,255,255,0.1) 0px,transparent 1px,transparent 40px,rgba(255,255,255,0.1) 41px),repeating-linear-gradient(90deg,rgba(255,255,255,0.1) 0px,transparent 1px,transparent 40px,rgba(255,255,255,0.1) 41px)">
      </div>
    </div>

    <div class="relative w-full max-w-sm">
      <!-- 标题区 -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-14 h-14 bg-[#3a3a3c] border border-white/10 rounded-xl mb-4">
          <svg class="w-7 h-7 text-[#8b92ff]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <h1 class="font-serif font-semibold text-2xl text-white/95 tracking-tight">
          {{ portal === 'admin' ? '管理员端登录' : '员工端登录' }}
        </h1>
        <p class="text-xs text-white/40 mt-1">HR Management System</p>
      </div>

      <!-- 登录卡片 -->
      <div class="bg-[#2c2c2e] border border-white/8 rounded-xl p-6 md:p-8">
        <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
          <el-form-item prop="username">
            <template #label>
              <span class="text-xs text-white/55 font-medium uppercase tracking-widest">用户名</span>
            </template>
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              prefix-icon="User"
              size="large"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item prop="password" style="margin-top:16px">
            <template #label>
              <span class="text-xs text-white/55 font-medium uppercase tracking-widest">密码</span>
            </template>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              size="large"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <div style="margin-top:24px">
            <el-button
              type="primary"
              size="large"
              style="width:100%;border-radius:8px;font-weight:600;letter-spacing:0.05em"
              :loading="loading"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </div>
        </el-form>
      </div>

      <!-- 底部 -->

      <p class="text-center mt-2">
        <router-link to="/" class="text-xs text-white/25 hover:text-white/50 transition-colors no-underline">
          ← 返回入口选择
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)

// 读取入口类型（来自 Landing 页的 ?portal=employee|admin）
const portal = computed(() => route.query.portal || 'employee')

const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    ElMessage.success('登录成功')
    // 根据角色和入口类型决定跳转目标
    if (auth.isManager && portal.value === 'admin') {
      router.push('/admin/dashboard')
    } else {
      router.push('/employee/dashboard')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>
