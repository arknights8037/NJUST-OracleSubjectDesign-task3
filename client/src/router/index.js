/**
 * Vue Router 路由配置
 *
 * 路由分为三类：
 *   - 公开路由（meta.public）：无需登录即可访问
 *   - 员工端（/employee）：所有已登录用户均可访问，移动端适配
 *   - 管理员端（/admin）：仅 manager/admin 角色可访问，桌面侧边栏布局
 *
 * 全局导航守卫：未登录 → /login；员工访问管理员页 → /employee/dashboard
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // 入口选择页
  { path: '/', component: () => import('@/views/Landing.vue'), meta: { public: true } },
  // 登录页（通过 ?portal=employee|admin 传递入口类型）
  { path: '/login', component: () => import('@/views/Login.vue'), meta: { public: true } },

  // ── 员工端（所有已登录用户均可访问，手机适配）──────────────────
  {
    path: '/employee',
    component: () => import('@/views/EmployeeLayout.vue'),
    redirect: '/employee/dashboard',
    children: [
      { path: 'dashboard',  component: () => import('@/views/Dashboard.vue'),  meta: { title: '首页' } },
      { path: 'attendance', component: () => import('@/views/Attendance.vue'), meta: { title: '打卡' } },
      { path: 'salary',     component: () => import('@/views/Salary.vue'),     meta: { title: '工资' } },
      { path: 'profile',    component: () => import('@/views/MyProfile.vue'),  meta: { title: '我的' } },
    ],
  },

  // ── 管理员端（仅 manager/admin 可访问，桌面侧边栏）────────────
  {
    path: '/admin',
    component: () => import('@/views/Layout.vue'),
    redirect: '/admin/dashboard',
    meta: { manager: true },
    children: [
      { path: 'dashboard',              component: () => import('@/views/Dashboard.vue'),        meta: { title: '首页仪表盘' } },
      { path: 'employees',              component: () => import('@/views/Employees.vue'),         meta: { title: '员工档案' } },
      { path: 'employees/:id/history',  component: () => import('@/views/EmployeeHistory.vue'),  meta: { title: '变动历史' } },
      { path: 'attendance-confirm',     component: () => import('@/views/AttendanceConfirm.vue'), meta: { title: '考勤确认' } },
      { path: 'salary-manage',          component: () => import('@/views/SalaryManage.vue'),      meta: { title: '工资单管理' } },
      { path: 'departments',            component: () => import('@/views/Departments.vue'),       meta: { title: '部门管理' } },
      { path: 'levels',                 component: () => import('@/views/SalaryLevels.vue'),      meta: { title: '级别工资配置' } },
      { path: 'penalty',                component: () => import('@/views/PenaltyConfig.vue'),     meta: { title: '罚款配置' } },
      { path: 'statistics',             component: () => import('@/views/Statistics.vue'),        meta: { title: '统计报表' } },
      { path: 'history',                component: () => import('@/views/AllHistory.vue'),        meta: { title: '变动历史查询' } },
    ],
  },

  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.public) return next()
  if (!auth.isLoggedIn) return next('/login')
  // 非管理员不可进入管理员端，转回员工端
  if (to.path.startsWith('/admin') && !auth.isManager) return next('/employee/dashboard')
  next()
})

export default router
