<template>
  <div class="space-y-3 md:space-y-4">
    <div v-if="auth.isManager" class="flex flex-wrap items-center gap-2 text-xs text-white/55">
      <span class="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5">
        {{ today }}
      </span>
      <span class="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5">
        <span class="h-2 w-2 rounded-full bg-[#4ade80]"></span>
        工资总额 {{ totalSalaryText }}
      </span>
      <span class="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5">
        最大部门 {{ topDepartmentName }}
      </span>
      <span class="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5">
        健康度 {{ attendanceHealthRate }}
      </span>
    </div>

    <!-- 统计卡片 -->
    <div v-if="auth.isManager" class="grid grid-cols-2 xl:grid-cols-4 gap-3 md:gap-4">
      <div v-for="item in metricCards" :key="item.label" class="rounded-2xl border border-white/8 bg-[#2c2c2e] px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.03)]">
        <div class="flex items-center justify-between gap-3">
          <div>
            <p class="text-[11px] text-white/42 uppercase tracking-[0.18em] font-medium">{{ item.label }}</p>
            <p class="mt-1.5 text-2xl font-semibold text-white/94">{{ item.value }}</p>
          </div>
          <span class="inline-flex h-9 w-9 items-center justify-center rounded-2xl border border-white/8 text-[11px]" :style="{ backgroundColor: item.badgeBackground, color: item.badgeColor }">
            {{ item.badge }}
          </span>
        </div>
      </div>
    </div>

    <div v-if="auth.isManager" class="flex flex-col gap-4">
      <!-- 第一行 -->
      <div class="grid grid-cols-1 gap-4 xl:grid-cols-12 items-stretch">
        <section class="flex flex-col overflow-hidden rounded-2xl border border-white/8 bg-[#2c2c2e] xl:col-span-5">
          <div class="shrink-0 px-4 md:px-5 py-3 border-b border-white/8 flex items-center justify-between gap-3">
            <h2 class="text-sm font-semibold text-white/92">部门工资趋势</h2>
            <span class="text-[11px] text-white/35">趋势</span>
          </div>
          <div ref="salaryChartRef" class="flex-1 min-h-[220px] px-2 md:px-3"></div>
        </section>

        <section class="flex flex-col overflow-hidden rounded-2xl border border-white/8 bg-[#2c2c2e] xl:col-span-4">
          <div class="shrink-0 px-4 md:px-6 py-3 border-b border-white/8 flex items-center justify-between gap-3">
            <h2 class="text-sm font-semibold text-white/92">部门人员分布</h2>
            <span class="text-[11px] text-white/35">实时统计</span>
          </div>
          <div ref="headcountChartRef" class="flex-1 min-h-[220px] px-2 md:px-3"></div>
        </section>

        <aside class="flex flex-col overflow-hidden rounded-2xl border border-white/8 bg-[#2c2c2e] xl:col-span-3">
          <div class="shrink-0 px-4 md:px-5 py-3 border-b border-white/8">
            <h2 class="text-sm font-semibold text-white/92">运营摘要</h2>
          </div>
          <div class="flex-1 grid grid-cols-1 gap-2.5 p-4 content-start">
            <div v-for="item in summaryCards" :key="item.label" class="rounded-lg border border-white/8 bg-white/[0.03] px-3 py-2 flex items-center justify-between gap-2">
              <p class="text-[11px] text-white/42">{{ item.label }}</p>
              <p class="text-sm font-semibold" :style="{ color: item.color || 'rgba(255,255,255,0.92)' }">{{ item.value }}</p>
            </div>
          </div>
        </aside>
      </div>

      <!-- 第二行：等高 -->
      <div class="grid grid-cols-1 gap-4 xl:grid-cols-3 items-stretch">
        <section class="flex flex-col overflow-hidden rounded-2xl border border-white/8 bg-[#2c2c2e]">
          <div class="shrink-0 px-4 md:px-5 py-3 border-b border-white/8 flex items-center justify-between gap-3">
            <h2 class="text-sm font-semibold text-white/92">月度考勤结构</h2>
            <span class="text-[11px] text-white/35">占比</span>
          </div>
          <div ref="attendanceTrendChartRef" class="flex-1 min-h-[200px] px-2 md:px-3"></div>
        </section>

        <section class="flex flex-col overflow-hidden rounded-2xl border border-white/8 bg-[#2c2c2e]">
          <div class="shrink-0 px-4 md:px-5 py-3 border-b border-white/8 flex items-center justify-between gap-3">
            <h2 class="text-sm font-semibold text-white/92">考勤指标</h2>
            <span class="text-[11px] text-white/35">明细</span>
          </div>
          <div class="flex-1 grid grid-cols-2 gap-3 p-4 content-start">
            <div v-for="item in attendanceSummaryCards" :key="item.label" class="rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3 flex items-center gap-3">
              <p class="text-xl font-semibold shrink-0" :style="{ color: item.color }">{{ item.value }}</p>
              <p class="text-xs text-white/42 leading-snug">{{ item.label }}</p>
            </div>
          </div>
        </section>

        <section class="flex flex-col overflow-hidden rounded-2xl border border-white/8 bg-[#2c2c2e]">
          <div class="shrink-0 px-4 md:px-5 py-3 border-b border-white/8 flex items-center justify-between gap-3">
            <h2 class="text-sm font-semibold text-white/92">部门排行</h2>
            <span class="text-[11px] text-white/32">Top {{ rankedDepartments.length }}</span>
          </div>
          <div class="flex-1 divide-y divide-white/[0.06]">
            <div v-for="dept in rankedDepartments" :key="dept.department_name" class="flex items-center gap-3 px-4 py-3">
              <span class="shrink-0 text-[11px] font-semibold text-white/28 w-5 text-center">{{ dept.rank }}</span>
              <span class="flex-1 truncate text-sm text-white/82">{{ dept.department_name }}</span>
              <div class="w-24 h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
                <div class="h-full rounded-full bg-gradient-to-r from-[#6b72ff] to-[#8ea2ff]" :style="{ width: `${dept.ratio}%` }"></div>
              </div>
              <span class="shrink-0 text-xs text-white/38 w-9 text-right">{{ dept.ratio.toFixed(0) }}%</span>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- 员工个人首页 -->
    <div v-if="!auth.isManager" class="flex flex-col gap-4">

      <!-- 打招呼 banner -->
      <div class="rounded-2xl bg-gradient-to-br from-[#1d1d2e] via-[#1a1a2c] to-[#1c1c2a] border border-[#6b72ff]/18 px-5 py-5 flex items-center justify-between">
        <div>
          <p class="text-base font-semibold text-white/92">{{ empGreeting }}，{{ auth.name }}</p>
          <p class="text-xs text-white/38 mt-1">{{ today }}</p>
        </div>
        <div class="w-11 h-11 rounded-full bg-[#2a2a3e] border border-[#6b72ff]/30 flex items-center justify-center text-sm font-bold text-[#c5c9ff] shrink-0">
          {{ auth.name?.charAt(0) }}
        </div>
      </div>

      <!-- 今日打卡 -->
      <div class="rounded-2xl border border-white/8 bg-[#2c2c2e] overflow-hidden">
        <div class="px-4 py-3 border-b border-white/8 flex items-center justify-between">
          <h2 class="text-sm font-semibold text-white/90">今日打卡</h2>
          <span v-if="empTodayAttend"
            class="text-[11px] px-2 py-0.5 rounded-full bg-[#152e1a] text-[#32d74b] border border-[#32d74b]/20">
            已签到
          </span>
          <span v-else class="text-[11px] text-white/28">未签到</span>
        </div>
        <div class="p-4 grid grid-cols-2 gap-3">
          <button
            @click="checkIn"
            :disabled="checking"
            class="flex items-center justify-center gap-2 py-3 bg-[#152e1a] border border-[#32d74b]/25 rounded-xl text-[#32d74b] text-sm font-medium hover:bg-[#1a3820] transition-colors disabled:opacity-50"
          >
            <el-icon><Clock /></el-icon>
            签到
          </button>
          <button
            @click="checkOut"
            :disabled="checking"
            class="flex items-center justify-center gap-2 py-3 bg-[#2e2200] border border-[#ffd60a]/20 rounded-xl text-[#ffd60a] text-sm font-medium hover:bg-[#3a2b00] transition-colors disabled:opacity-50"
          >
            <el-icon><Clock /></el-icon>
            签离
          </button>
        </div>
        <div v-if="empTodayAttend" class="px-4 pb-3 flex items-center gap-4 text-[11px] text-white/32">
          <span v-if="empTodayAttend.check_in_time">签到 {{ empTodayAttend.check_in_time?.slice(11, 16) }}</span>
          <span v-if="empTodayAttend.check_out_time">签离 {{ empTodayAttend.check_out_time?.slice(11, 16) }}</span>
        </div>
      </div>

      <!-- 本月摘要 -->
      <div class="grid grid-cols-2 gap-3">
        <div
          class="rounded-2xl border border-white/8 bg-[#2c2c2e] px-4 py-4 cursor-pointer hover:border-white/15 transition-colors"
          @click="$router.push('/employee/salary')"
        >
          <p class="text-[11px] text-white/40 uppercase tracking-wider mb-1.5">本月实发</p>
          <p class="text-xl font-semibold text-white/90">{{ empMonthSalaryText }}</p>
          <p class="text-[11px] text-[#32d74b]/55 mt-2">查看明细 →</p>
        </div>
        <div
          class="rounded-2xl border border-white/8 bg-[#2c2c2e] px-4 py-4 cursor-pointer hover:border-white/15 transition-colors"
          @click="$router.push('/employee/attendance')"
        >
          <p class="text-[11px] text-white/40 uppercase tracking-wider mb-1.5">本月出勤</p>
          <p class="text-xl font-semibold text-white/90">{{ empMonthAttendCount }} <span class="text-sm text-white/38 font-normal">天</span></p>
          <p class="text-[11px] text-white/28 mt-2">正常 {{ empMonthNormalCount }} · 迟到 {{ empMonthLateCount }}</p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { attendanceApi, deptApi, employeeApi, salaryApi, statsApi } from '@/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const stats = reactive({ activeEmployees: 0, depts: 0, salaryCount: 0, todayAttend: 0 })
const deptStats = ref([])
const deptSalaryStats = ref([])
const attendanceOverview = reactive({ normal: 0, late: 0, absent: 0, businessTrip: 0, outside: 0 })
const checking = ref(false)
const empSalary = ref(null)
const empAttendList = ref([])
const empGreeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})
const empTodayAttend = computed(() => {
  const d = new Date().toISOString().slice(0, 10)
  return empAttendList.value.find(r => (r.date || r.check_in_time || '').startsWith(d)) || null
})
const empMonthSalaryText = computed(() => {
  if (!empSalary.value) return '暂无数据'
  return `¥${Number(empSalary.value.total_salary || 0).toLocaleString('zh-CN')}`
})
const empMonthAttendCount = computed(() => empAttendList.value.length)
const empMonthNormalCount = computed(() => empAttendList.value.filter(r => r.status === 'normal').length)
const empMonthLateCount = computed(() => empAttendList.value.filter(r => r.status === 'late').length)
const headcountChartRef = ref(null)
const salaryChartRef = ref(null)
const attendanceTrendChartRef = ref(null)
let headcountChart
let salaryChart
let attendanceTrendChart

const today = computed(() => new Date().toLocaleDateString('zh-CN', { year:'numeric', month:'long', day:'numeric', weekday:'long' }))
const currentYearMonth = computed(() => new Date().toISOString().slice(0, 7))
const attendanceSummaryCards = computed(() => [
  { label: '正常', value: attendanceOverview.normal, color: '#7dd3fc', description: '按时完成签到签离' },
  { label: '迟到', value: attendanceOverview.late, color: '#fbbf24', description: '迟到但仍完成出勤' },
  { label: '缺勤', value: attendanceOverview.absent, color: '#f87171', description: '缺勤或超阈值迟到' },
  { label: '出差 / 外出', value: attendanceOverview.businessTrip + attendanceOverview.outside, color: '#a78bfa', description: '经确认的特殊状态' },
])
const topDepartment = computed(() => {
  return [...deptStats.value].sort((a, b) => Number(b.employee_count || 0) - Number(a.employee_count || 0))[0] || null
})
const topDepartmentName = computed(() => topDepartment.value?.department_name || '暂无数据')
const topDepartmentCount = computed(() => Number(topDepartment.value?.employee_count || 0))
const totalSalary = computed(() => {
  return deptSalaryStats.value.reduce((sum, item) => sum + Number(item.total_salary || 0), 0)
})
const totalSalaryText = computed(() => `¥${totalSalary.value.toLocaleString('zh-CN')}`)
const averageDepartmentCount = computed(() => {
  if (!stats.depts) return '0 人'
  return `${(stats.activeEmployees / stats.depts).toFixed(1)} 人`
})
const attendanceTotal = computed(() => {
  return attendanceOverview.normal + attendanceOverview.late + attendanceOverview.absent + attendanceOverview.businessTrip + attendanceOverview.outside
})
const attendanceHealthRate = computed(() => {
  if (!attendanceTotal.value) return '0%'
  return `${((attendanceOverview.normal / attendanceTotal.value) * 100).toFixed(1)}%`
})
const rankedDepartments = computed(() => {
  const max = Math.max(...deptStats.value.map(item => Number(item.employee_count || 0)), 0)
  return [...deptStats.value]
    .sort((a, b) => Number(b.employee_count || 0) - Number(a.employee_count || 0))
    .slice(0, 5)
    .map((item, index) => ({
      ...item,
      rank: String(index + 1).padStart(2, '0'),
      ratio: max ? Math.max(12, (Number(item.employee_count || 0) / max) * 100) : 0,
    }))
})
const metricCards = computed(() => [
  {
    label: '在职员工',
    value: stats.activeEmployees,
    hint: '当前处于 active 状态的员工数量',
    badge: 'EMP',
    badgeColor: '#c5c9ff',
    badgeBackground: 'rgba(107,114,255,0.14)',
  },
  {
    label: '部门数量',
    value: stats.depts,
    hint: '当前可参与统计的组织单元数量',
    badge: 'ORG',
    badgeColor: '#86efac',
    badgeBackground: 'rgba(74,222,128,0.14)',
  },
  {
    label: '本月工资记录',
    value: stats.salaryCount,
    hint: '已生成的月度工资记录总数',
    badge: 'PAY',
    badgeColor: '#fcd34d',
    badgeBackground: 'rgba(251,191,36,0.14)',
  },
  {
    label: '今日出勤',
    value: stats.todayAttend,
    hint: '按今日考勤记录汇总的实时人数',
    badge: 'ATT',
    badgeColor: '#7dd3fc',
    badgeBackground: 'rgba(96,165,250,0.14)',
  },
])
const summaryCards = computed(() => [
  {
    label: '最大部门',
    value: topDepartmentName.value,
    description: `${topDepartmentCount.value} 人在职`,
    color: '#c5c9ff',
  },
  {
    label: '部门均值',
    value: averageDepartmentCount.value,
    description: '平均每个部门在职人数',
  },
  {
    label: '考勤健康度',
    value: attendanceHealthRate.value,
    description: '正常考勤占本月考勤记录比例',
    color: '#86efac',
  },
])

onMounted(async () => {
  try {
    const depts = await deptApi.list()
    stats.depts = depts.data.length
    if (auth.isManager) {
      const emps = await employeeApi.list({ status: 'active' })
      stats.activeEmployees = emps.data.length
      const ds = await statsApi.deptHeadcount()
      deptStats.value = ds.data
      const salaryRes = await statsApi.deptSalary(currentYearMonth.value)
      deptSalaryStats.value = salaryRes.data
      stats.salaryCount = deptSalaryStats.value.reduce((sum, item) => sum + Number(item.employee_count || 0), 0)
      const attendanceRes = await statsApi.monthlyAttend(currentYearMonth.value)
      hydrateAttendanceOverview(attendanceRes.data)
      const todayStr = new Date().toISOString().slice(0, 10)
      const att = await attendanceApi.list({ start_date: todayStr, end_date: todayStr })
      stats.todayAttend = att.data.length
      await nextTick()
      initCharts()
      renderCharts()
    } else {
      const todayStr = new Date().toISOString().slice(0, 10)
      const ym = currentYearMonth.value
      const firstDay = ym + '-01'
      const [sr, ar] = await Promise.all([
        salaryApi.my(),
        attendanceApi.list({ start_date: firstDay, end_date: todayStr }),
      ])
      const thisMonth = sr.data.find(r => (r.year_month || '').slice(0, 7) === ym)
      empSalary.value = thisMonth || null
      empAttendList.value = ar.data || []
    }
  } catch {}

  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  disposeCharts()
})

function hydrateAttendanceOverview(records) {
  attendanceOverview.normal = records.reduce((sum, item) => sum + Number(item.normal_days || 0), 0)
  attendanceOverview.late = records.reduce((sum, item) => sum + Number(item.late_days || 0), 0)
  attendanceOverview.absent = records.reduce((sum, item) => sum + Number(item.absent_days || 0), 0)
  attendanceOverview.businessTrip = records.reduce((sum, item) => sum + Number(item.trip_days || 0), 0)
  attendanceOverview.outside = records.reduce((sum, item) => sum + Number(item.outside_days || 0), 0)
}

function initCharts() {
  if (!auth.isManager) return
  if (headcountChartRef.value && !headcountChart) {
    headcountChart = echarts.init(headcountChartRef.value)
  }
  if (salaryChartRef.value && !salaryChart) {
    salaryChart = echarts.init(salaryChartRef.value)
  }
  if (attendanceTrendChartRef.value && !attendanceTrendChart) {
    attendanceTrendChart = echarts.init(attendanceTrendChartRef.value)
  }
}

function renderCharts() {
  if (!auth.isManager) return

  headcountChart?.setOption({
    backgroundColor: 'transparent',
    grid: { left: 18, right: 18, top: 18, bottom: 18, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(28,28,30,0.95)',
      borderColor: 'rgba(255,255,255,0.08)',
      textStyle: { color: 'rgba(255,255,255,0.88)' },
    },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      axisLabel: { color: 'rgba(255,255,255,0.40)' },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.12)' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'category',
      data: deptStats.value.map(item => item.department_name),
      axisLabel: { color: 'rgba(255,255,255,0.62)' },
      axisTick: { show: false },
      axisLine: { show: false },
    },
    series: [{
      type: 'bar',
      data: deptStats.value.map(item => item.employee_count),
      barWidth: 18,
      itemStyle: {
        borderRadius: [0, 10, 10, 0],
        color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
          { offset: 0, color: '#8ea2ff' },
          { offset: 1, color: '#5b66df' },
        ]),
      },
      label: {
        show: true,
        position: 'right',
        color: 'rgba(255,255,255,0.72)',
      },
    }],
  })

  salaryChart?.setOption({
    backgroundColor: 'transparent',
    grid: { left: 18, right: 18, top: 22, bottom: 18, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(28,28,30,0.95)',
      borderColor: 'rgba(255,255,255,0.08)',
      textStyle: { color: 'rgba(255,255,255,0.88)' },
      valueFormatter: value => `¥${Number(value || 0).toLocaleString('zh-CN')}`,
    },
    xAxis: {
      type: 'category',
      data: deptSalaryStats.value.map(item => item.department_name),
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.12)' } },
      axisLabel: { color: 'rgba(255,255,255,0.56)' },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      axisLabel: {
        color: 'rgba(255,255,255,0.48)',
        formatter: value => `¥${Number(value / 1000).toFixed(value >= 10000 ? 0 : 1)}k`,
      },
    },
    series: [{
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 10,
      data: deptSalaryStats.value.map(item => Number(item.total_salary || 0)),
      lineStyle: { width: 3, color: '#4ade80' },
      itemStyle: { color: '#86efac', borderColor: '#183924', borderWidth: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(74, 222, 128, 0.35)' },
          { offset: 1, color: 'rgba(74, 222, 128, 0.02)' },
        ]),
      },
    }],
  })

  attendanceTrendChart?.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(28,28,30,0.95)',
      borderColor: 'rgba(255,255,255,0.08)',
      textStyle: { color: 'rgba(255,255,255,0.88)' },
      formatter: ({ name, value, percent }) => `${name}<br/>${value} 天 (${percent}%)`,
    },
    legend: {
      bottom: 10,
      left: 'center',
      textStyle: { color: 'rgba(255,255,255,0.56)' },
      itemWidth: 10,
      itemHeight: 10,
    },
    series: [{
      type: 'pie',
      radius: ['52%', '74%'],
      center: ['50%', '42%'],
      avoidLabelOverlap: true,
      label: { show: false },
      labelLine: { show: false },
      emphasis: {
        label: {
          show: true,
          formatter: '{b}\n{d}%',
          color: 'rgba(255,255,255,0.9)',
          fontSize: 14,
          fontWeight: 600,
        },
      },
      data: [
        { value: attendanceOverview.normal, name: '正常', itemStyle: { color: '#60a5fa' } },
        { value: attendanceOverview.late, name: '迟到', itemStyle: { color: '#fbbf24' } },
        { value: attendanceOverview.absent, name: '缺勤', itemStyle: { color: '#f87171' } },
        { value: attendanceOverview.businessTrip, name: '出差', itemStyle: { color: '#34d399' } },
        { value: attendanceOverview.outside, name: '外出', itemStyle: { color: '#a78bfa' } },
      ],
    }],
  })
}

function resizeCharts() {
  headcountChart?.resize()
  salaryChart?.resize()
  attendanceTrendChart?.resize()
}

function disposeCharts() {
  headcountChart?.dispose()
  salaryChart?.dispose()
  attendanceTrendChart?.dispose()
  headcountChart = null
  salaryChart = null
  attendanceTrendChart = null
}

async function checkIn() {
  checking.value = true
  try {
    await attendanceApi.checkIn({})
    ElMessage.success('签到成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '签到失败')
  } finally {
    checking.value = false
  }
}

async function checkOut() {
  checking.value = true
  try {
    await attendanceApi.checkOut({})
    ElMessage.success('签离成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '签离失败')
  } finally {
    checking.value = false
  }
}
</script>
