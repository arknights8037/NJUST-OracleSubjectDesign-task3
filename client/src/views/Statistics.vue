<template>
  <div class="h-full flex flex-col">
    <div class="flex-1 min-h-0 flex flex-col bg-[#2c2c2e] border border-white/8 rounded-xl overflow-hidden stats-card">
      <el-tabs v-model="activeTab" class="stats-tabs" style="padding:0 20px">
        <el-tab-pane label="部门人员统计" name="headcount">
          <div class="stats-tab-body">
            <div class="shrink-0 flex gap-2 mb-3">
              <el-button size="small" @click="loadHeadcount">刷新</el-button>
              <el-button type="success" size="small" @click="exportHeadcount">导出 Excel</el-button>
            </div>
            <div ref="hcBodyRef" class="flex-1 min-h-0">
              <el-table :data="headcountData" border :height="hcTableHeight" style="width:100%">
                <el-table-column prop="department_name" label="部门" min-width="120" />
                <el-table-column prop="employee_count" label="在职人数" min-width="100" />
              </el-table>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="月度工资统计" name="salary">
          <div class="stats-tab-body">
            <div class="shrink-0 flex flex-wrap gap-3 items-end mb-3">
              <div>
                <p class="text-xs text-white/45 mb-1.5">年月</p>
                <el-date-picker v-model="salaryMonth" type="month" value-format="YYYY-MM" />
              </div>
              <div class="flex gap-2">
                <el-button type="primary" size="small" @click="loadSalaryStat">查询</el-button>
                <el-button type="success" size="small" @click="exportSalary">导出 Excel</el-button>
              </div>
            </div>
            <div ref="salaryBodyRef" class="flex-1 min-h-0">
              <el-table :data="salaryData" border show-summary :summary-method="salarySummary" :height="salaryTableHeight" style="width:100%">
                <el-table-column prop="department_name" label="部门" min-width="120" />
                <el-table-column prop="employee_count" label="人数" min-width="80" />
                <el-table-column prop="total_salary" label="工资总额" min-width="120" :formatter="fmtMoney" />
              </el-table>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="月度考勤统计" name="attend">
          <div class="stats-tab-body">
            <div class="shrink-0 flex flex-wrap gap-3 items-end mb-3">
              <div>
                <p class="text-xs text-white/45 mb-1.5">年月</p>
                <el-date-picker v-model="attendMonth" type="month" value-format="YYYY-MM" />
              </div>
              <div class="flex gap-2">
                <el-button type="primary" size="small" @click="loadAttendStat">查询</el-button>
                <el-button type="success" size="small" @click="exportAttend">导出 Excel</el-button>
                <el-button size="small" @click="printAttend">打印</el-button>
              </div>
            </div>
            <div ref="attendBodyRef" class="flex-1 min-h-0">
              <el-table :data="attendData" border id="attend-stat-table" :height="attendTableHeight" style="width:100%">
                <el-table-column prop="employee_name" label="员工" min-width="80" />
                <el-table-column prop="total_days" label="出勤天数" min-width="80" />
                <el-table-column prop="normal_days" label="正常" min-width="65" />
                <el-table-column prop="late_days" label="迟到" min-width="65" />
                <el-table-column prop="absent_days" label="缺勤" min-width="65" />
                <el-table-column prop="trip_days" label="出差" min-width="65" />
                <el-table-column prop="outside_days" label="外出" min-width="65" />
                <el-table-column prop="total_penalty" label="罚款合计" min-width="90" :formatter="fmtMoney" />
              </el-table>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { statsApi } from '@/api'
import { useTableHeight } from '@/composables/useTableHeight'
import * as XLSX from 'xlsx'

const activeTab = ref('headcount')
const headcountData = ref([])
const salaryData = ref([])
const attendData = ref([])
const salaryMonth = ref(new Date().toISOString().slice(0, 7))
const attendMonth = ref(new Date().toISOString().slice(0, 7))

const hcBodyRef = ref(null)
const hcTableHeight = useTableHeight(hcBodyRef)
const salaryBodyRef = ref(null)
const salaryTableHeight = useTableHeight(salaryBodyRef)
const attendBodyRef = ref(null)
const attendTableHeight = useTableHeight(attendBodyRef)

onMounted(loadHeadcount)

async function loadHeadcount() {
  headcountData.value = (await statsApi.deptHeadcount()).data
}
async function loadSalaryStat() {
  salaryData.value = (await statsApi.deptSalary(salaryMonth.value)).data
}
async function loadAttendStat() {
  attendData.value = (await statsApi.monthlyAttend(attendMonth.value)).data
}

function fmtMoney(_, __, val) { return val ? `¥${Number(val).toFixed(2)}` : '¥0.00' }

function salarySummary({ data }) {
  const total = data.reduce((s, r) => s + Number(r.total_salary || 0), 0)
  return ['合计', '', `¥${total.toFixed(2)}`]
}

function exportHeadcount() {
  exportXlsx(headcountData.value, ['department_name', 'employee_count'], ['部门', '在职人数'], '部门人员统计')
}
function exportSalary() {
  exportXlsx(salaryData.value, ['department_name', 'employee_count', 'total_salary'], ['部门', '人数', '工资总额'], `工资统计_${salaryMonth.value}`)
}
function exportAttend() {
  exportXlsx(attendData.value,
    ['employee_name', 'total_days', 'normal_days', 'late_days', 'absent_days', 'trip_days', 'outside_days', 'total_penalty'],
    ['员工', '出勤', '正常', '迟到', '缺勤', '出差', '外出', '罚款'],
    `考勤统计_${attendMonth.value}`)
}

function exportXlsx(data, keys, headers, filename) {
  const rows = data.map(r => {
    const obj = {}
    keys.forEach((k, i) => { obj[headers[i]] = r[k] })
    return obj
  })
  const ws = XLSX.utils.json_to_sheet(rows)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, filename)
  XLSX.writeFile(wb, `${filename}.xlsx`)
}

function printAttend() { window.print() }
</script>

<style scoped>
.stats-card .stats-tabs {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.stats-card :deep(.el-tabs__content) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
.stats-card :deep(.el-tab-pane) {
  height: 100%;
}
.stats-tab-body {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding-bottom: 12px;
}
</style>

<style>
@media print {
  .el-header, .el-aside, .el-card__header .el-button { display: none !important; }
}
</style>
