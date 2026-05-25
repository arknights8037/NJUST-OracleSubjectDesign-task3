<template>
  <div class="flex flex-col bg-[#1c1c1e] overflow-hidden" style="height:100dvh">

    <!-- 顶部导航栏 -->
    <header class="shrink-0 flex items-center justify-between px-4 h-12
                   bg-[#2c2c2e]/90 backdrop-blur-xl border-b border-white/8 z-10">
      <div class="flex items-center gap-2.5">
        <div class="w-7 h-7 bg-[#2a2a3e] border border-[#6b72ff]/30 rounded-full flex items-center justify-center shrink-0 text-[11px] font-semibold text-[#c5c9ff]">
          {{ auth.name?.charAt(0) }}
        </div>
        <div>
          <p class="text-sm font-medium text-white/90 leading-none">{{ greeting }}，{{ auth.name }}</p>
          <p class="text-[10px] text-white/35 mt-0.5 leading-none">{{ todayShort }}</p>
        </div>
      </div>
      <button
        @click="handleLogout"
        class="p-1.5 rounded-lg text-white/35 hover:text-white/65 hover:bg-white/8 transition-colors"
        title="退出登录"
      >
        <el-icon class="text-base"><SwitchButton /></el-icon>
      </button>
    </header>

    <!-- 内容区域 -->
    <main class="flex-1 overflow-y-auto overflow-x-hidden" style="padding-bottom:64px">
      <div class="p-4">
        <router-view />
      </div>
    </main>

    <!-- 底部标签栏 -->
    <nav class="fixed bottom-0 inset-x-0 h-16 bg-[#2c2c2e]/90 backdrop-blur-xl
                border-t border-white/8 flex items-center justify-around px-2 z-50
                safe-area-inset-bottom">
      <router-link
        v-for="tab in tabs"
        :key="tab.path"
        :to="tab.path"
        class="flex flex-col items-center justify-center gap-0.5 px-4 py-1.5 rounded-xl
               transition-all duration-150 no-underline min-w-[56px]"
        :class="isActive(tab.path)
          ? 'bg-[#6b72ff]/16 text-white shadow-[inset_0_0_0_1px_rgba(107,114,255,0.24)]'
          : 'text-white/35 hover:bg-white/5 hover:text-white/70'"
      >
        <el-icon class="text-[22px]" :class="isActive(tab.path) ? 'text-[#c5c9ff]' : ''"><component :is="tab.icon" /></el-icon>
        <span class="text-[10px] font-medium leading-none">{{ tab.label }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})
const todayShort = computed(() => new Date().toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'short' }))

const tabs = [
  { path: '/employee/dashboard', icon: 'Odometer', label: '首页' },
  { path: '/employee/attendance', icon: 'Clock', label: '打卡' },
  { path: '/employee/salary', icon: 'Money', label: '工资' },
  { path: '/employee/profile', icon: 'User', label: '我的' },
]

function isActive(path) {
  return route.path === path || route.path.startsWith(path + '/')
}

function handleLogout() {
  auth.logout()
  ElMessage.success('已退出')
  router.push('/')
}
</script>
