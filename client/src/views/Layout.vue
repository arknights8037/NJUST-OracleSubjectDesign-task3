<template>
  <div class="flex h-screen overflow-hidden bg-[#1c1c1e]">

    <!-- 侧边栏 -->
    <aside
      class="shrink-0 flex flex-col border-r border-white/8 overflow-hidden
             backdrop-blur-xl transition-[width] duration-200"
      :class="collapsed ? 'w-16' : 'w-[220px]'"
      style="background:rgba(28,28,30,0.95)"
    >
      <!-- Logo 区 -->
      <div class="flex items-center gap-3 px-3.5 min-h-[56px] border-b border-white/8 shrink-0">
        <div class="shrink-0 w-8 h-8 bg-[#6b72ff] rounded-lg flex items-center justify-center">
          <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <span v-if="!collapsed" class="text-[13px] font-semibold text-white/90 whitespace-nowrap overflow-hidden">
          人事管理系统
        </span>
      </div>

      <!-- 导航列表 -->
      <nav class="flex-1 overflow-y-auto overflow-x-hidden py-2.5 px-2 flex flex-col gap-0.5
                  [&::-webkit-scrollbar]:hidden">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="group relative flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[13px]
                 no-underline cursor-pointer whitespace-nowrap overflow-hidden transition-all duration-150"
          :class="isActive(item.path)
            ? 'bg-[#6b72ff]/16 text-white font-medium shadow-[inset_0_0_0_1px_rgba(107,114,255,0.28)]'
            : 'text-white/50 hover:bg-white/7 hover:text-white/85'"
        >
          <!-- 激活左侧指示条 -->
          <span v-if="isActive(item.path)"
                class="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-4 bg-[#6b72ff] rounded-r">
          </span>

          <el-icon class="shrink-0 text-[15px]" :class="isActive(item.path) ? 'text-[#c5c9ff]' : ''"><component :is="item.icon" /></el-icon>
          <span v-if="!collapsed" class="overflow-hidden text-ellipsis">{{ item.label }}</span>

          <!-- 折叠时的浮动提示 -->
          <span v-if="collapsed"
                class="absolute left-[calc(100%+10px)] top-1/2 -translate-y-1/2
                       bg-[#3a3a3c] border border-white/10 rounded-lg px-2.5 py-1
                       text-xs text-white/90 whitespace-nowrap pointer-events-none
                       opacity-0 group-hover:opacity-100 transition-opacity duration-150 z-[200]">
            {{ item.label }}
          </span>
        </router-link>

        <!-- 管理分组分隔线 -->
        <template v-if="auth.isManager">
          <div class="px-2.5 pt-4 pb-1 shrink-0">
            <span v-if="!collapsed" class="text-[10px] font-semibold tracking-[0.08em] uppercase text-white/28">
              管理
            </span>
          </div>
          <router-link
            v-for="item in managerMenuItems"
            :key="item.path"
            :to="item.path"
            class="group relative flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[13px]
                   no-underline cursor-pointer whitespace-nowrap overflow-hidden transition-all duration-150"
            :class="isActive(item.path)
              ? 'bg-[#6b72ff]/16 text-white font-medium shadow-[inset_0_0_0_1px_rgba(107,114,255,0.28)]'
              : 'text-white/50 hover:bg-white/7 hover:text-white/85'"
          >
            <span v-if="isActive(item.path)"
                  class="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-4 bg-[#6b72ff] rounded-r">
            </span>
            <el-icon class="shrink-0 text-[15px]" :class="isActive(item.path) ? 'text-[#c5c9ff]' : ''"><component :is="item.icon" /></el-icon>
            <span v-if="!collapsed" class="overflow-hidden text-ellipsis">{{ item.label }}</span>
            <span v-if="collapsed"
                  class="absolute left-[calc(100%+10px)] top-1/2 -translate-y-1/2
                         bg-[#3a3a3c] border border-white/10 rounded-lg px-2.5 py-1
                         text-xs text-white/90 whitespace-nowrap pointer-events-none
                         opacity-0 group-hover:opacity-100 transition-opacity duration-150 z-[200]">
              {{ item.label }}
            </span>
          </router-link>
        </template>
      </nav>

      <!-- 用户信息 -->
      <div class="shrink-0 border-t border-white/8 px-3 py-3"
           :class="collapsed ? 'flex flex-col items-center gap-2' : 'flex items-center gap-2'">
        <div class="shrink-0 w-[30px] h-[30px] bg-[#3a3a3c] border border-white/10 rounded-lg
                    flex items-center justify-center text-white/55 text-sm">
          <el-icon><User /></el-icon>
        </div>
        <div v-if="!collapsed" class="flex-1 min-w-0">
          <p class="m-0 text-xs font-medium text-white/88 truncate">{{ auth.name }}</p>
          <p class="m-0 mt-0.5 text-[11px] text-white/35 truncate">{{ roleLabel }}</p>
        </div>
        <!-- 设置按鈕（管理员可见） -->
        <button
          v-if="auth.isManager"
          class="shrink-0 w-[28px] h-[28px] flex items-center justify-center rounded-lg
                 text-white/40 transition-colors hover:bg-white/10 hover:text-[#6b72ff]"
          title="系统设置"
          @click="showSettings = true"
        >
          <el-icon class="text-sm"><Tools /></el-icon>
        </button>
      </div>
    </aside>

    <!-- 主区域 -->
    <div class="flex-1 min-w-0 flex flex-col overflow-hidden">

      <!-- 顶栏 -->
      <header class="shrink-0 h-14 flex items-center gap-3 px-5 bg-[#2c2c2e] border-b border-white/8">
        <button
          class="shrink-0 w-8 h-8 flex items-center justify-center rounded-lg
                 text-white/50 text-base transition-colors hover:bg-white/8 hover:text-white/90"
          @click="collapsed = !collapsed"
        >
          <el-icon><component :is="collapsed ? 'Expand' : 'Fold'" /></el-icon>
        </button>
        <span class="text-sm text-white/55">{{ pageTitle }}</span>
        <div class="flex-1" />
        <!-- 全局搜索 -->
        <button
          class="hidden sm:flex w-[200px] shrink-0 items-center gap-2 px-3 py-1.5
                 rounded-lg bg-[#1c1c1e] border border-white/8
                 text-white/35 text-xs transition-colors hover:border-white/16 hover:text-white/55"
          @click="showSearch = true"
        >
          <el-icon class="shrink-0"><Search /></el-icon>
          <span class="flex-1 text-left">搜索…</span>
          <kbd class="text-[10px] px-1 py-0.5 rounded bg-white/8 shrink-0">Ctrl K</kbd>
        </button>
        <div class="shrink-0 flex items-center gap-3">
          <span class="text-xs text-white/38">欢迎，{{ auth.name }}</span>
          <button
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#3a3a3c]
                   border border-white/10 text-white/65 text-xs
                   transition-colors hover:text-white/90 hover:border-white/18"
            @click="handleLogout"
          >
            <el-icon><SwitchButton /></el-icon>
            <span>退出</span>
          </button>
        </div>
      </header>

      <!-- 内容区 -->
      <main class="flex-1 min-h-0 overflow-hidden bg-[#1c1c1e]">
        <div class="h-full px-4 py-3 md:px-5 md:py-4 overflow-y-auto">
          <router-view />
        </div>
      </main>

      <global-search v-model="showSearch" />

      <!-- 系统设置对话框 -->
      <el-dialog v-model="showSettings" title="系统设置" width="480px">
        <div class="space-y-4">
          <div class="flex items-center gap-2 pb-3 border-b border-white/10">
            <el-icon class="text-[#6b72ff] text-lg"><Files /></el-icon>
            <span class="font-medium text-white/90">批量写入测试数据</span>
          </div>
          <el-form label-width="100px">
            <el-form-item label="员工数量">
              <el-input-number v-model="seedForm.employee_count" :min="1" :max="100" class="w-full" />
            </el-form-item>
            <el-form-item label="目标月份">
              <el-date-picker v-model="seedForm.year_month" type="month" value-format="YYYY-MM" class="w-full" />
            </el-form-item>
            <el-form-item label="生成考勤">
              <el-switch v-model="seedForm.include_attendance" />
            </el-form-item>
            <el-form-item label="生成工资">
              <el-switch v-model="seedForm.generate_salary" :disabled="!seedForm.include_attendance" />
            </el-form-item>
          </el-form>
          <div v-if="seedResult"
               class="rounded-lg bg-white/5 border border-white/10 p-3 text-sm text-white/70 space-y-1">
            <p>已写入 {{ seedResult.employee_count }} 名员工，{{ seedResult.attendance_count }} 条考勤，{{ seedResult.salary_count }} 条工资记录。</p>
            <p>数据月份：{{ seedResult.year_month }}｜默认密码：{{ seedResult.initial_password }}</p>
            <p>账号示例：{{ seedResult.usernames.slice(0, 4).join('、') }}<span v-if="seedResult.usernames.length > 4"> 等</span></p>
          </div>
          <p class="text-xs text-white/35">初始密码固定为 test123456，测试完毕后请及时清理数据。</p>
        </div>
        <template #footer>
          <el-button @click="showSettings = false">关闭</el-button>
          <el-button type="primary" :loading="seedLoading" @click="doSeedTestData">开始写入</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Tools, Files } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { employeeApi } from '@/api'
import GlobalSearch from '@/components/GlobalSearch.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const collapsed = ref(false)
const showSearch = ref(false)
const showSettings = ref(false)
const seedLoading = ref(false)
const seedResult = ref(null)
const seedForm = reactive({
  employee_count: 12,
  year_month: new Date().toISOString().slice(0, 7),
  include_attendance: true,
  generate_salary: true,
})

async function doSeedTestData() {
  seedLoading.value = true
  try {
    const payload = {
      employee_count: seedForm.employee_count,
      year_month: seedForm.year_month,
      include_attendance: seedForm.include_attendance,
      generate_salary: seedForm.include_attendance && seedForm.generate_salary,
    }
    const { data } = await employeeApi.seedTestData(payload)
    seedResult.value = data
    ElMessage.success('测试数据写入完成')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '写入测试数据失败')
  } finally {
    seedLoading.value = false
  }
}

const roleLabel = computed(() => {
  const m = { admin: '管理员', manager: '部门经理', employee: '员工' }
  return m[auth.role] || auth.role
})

const menuItems = [
  { path: '/admin/dashboard', icon: 'Odometer', label: '首页仪表盘' },
]

const managerMenuItems = [
  { path: '/admin/employees',          icon: 'Management',     label: '员工档案' },
  { path: '/admin/history',            icon: 'Document',       label: '变动历史' },
  { path: '/admin/attendance-confirm', icon: 'Calendar',       label: '考勤确认' },
  { path: '/admin/salary-manage',      icon: 'CreditCard',     label: '工资单管理' },
  { path: '/admin/departments',        icon: 'OfficeBuilding', label: '部门管理' },
  { path: '/admin/levels',             icon: 'Setting',        label: '级别配置' },
  { path: '/admin/penalty',            icon: 'Warning',        label: '罚款配置' },
  { path: '/admin/statistics',         icon: 'DataAnalysis',   label: '统计报表' },
]

const allMenuItems = [...menuItems, ...managerMenuItems]

const pageTitle = computed(() => {
  return route.meta.title || allMenuItems.find(i => route.path === i.path || route.path.startsWith(i.path + '/'))?.label || ''
})

function isActive(path) {
  return route.path === path || route.path.startsWith(path + '/')
}

function handleLogout() {
  auth.logout()
  ElMessage.success('已退出')
  router.push('/')
}
</script>

