<template>
  <div class="h-full flex flex-col gap-3 md:gap-4">
    <!-- 表格卡片 -->
    <div class="flex-1 min-h-0 flex flex-col bg-[#2c2c2e] border border-white/8 rounded-xl overflow-hidden">
      <div class="shrink-0 px-4 md:px-6 py-2.5 border-b border-white/8 flex flex-wrap items-center gap-3">
        <h2 class="font-semibold text-sm text-white/90 shrink-0">{{ yearMonth }} 工资单</h2>
        <div class="flex-1" />
        <div class="flex flex-wrap items-center gap-2">
          <el-date-picker v-model="yearMonth" type="month" value-format="YYYY-MM" placeholder="选择月份" style="width:170px" />
          <el-button type="primary" size="small" @click="generateSalary" :loading="generating">批量生成工资单</el-button>
          <el-button size="small" @click="loadData">查询</el-button>
          <el-button type="success" size="small" @click="exportExcel">导出 Excel</el-button>
          <el-button size="small" @click="printTable">打印</el-button>
        </div>
      </div>
      <div ref="tableBodyRef" class="flex-1 min-h-0">
        <el-table :data="pagedRecords" border v-loading="loading" :height="tableHeight" id="salary-table" style="width:100%">
          <el-table-column prop="employee_name" label="员工" min-width="80" sortable />
          <el-table-column prop="department_name" label="部门" min-width="85" sortable show-overflow-tooltip />
          <el-table-column prop="level_name" label="级别" min-width="80" sortable show-overflow-tooltip />
          <el-table-column prop="year_month" label="年月" min-width="85" sortable />
          <el-table-column prop="base_salary" label="基本工资" min-width="95" sortable :formatter="fmtMoney" />
          <el-table-column prop="bonus" label="奖金" min-width="80" sortable :formatter="fmtMoney" />
          <el-table-column prop="penalty" label="罚款扣除" min-width="90" sortable :formatter="fmtMoney" />
          <el-table-column prop="total_salary" label="实发工资" min-width="95" sortable :formatter="fmtMoney" />
          <el-table-column prop="bonus_remark" label="奖金备注" min-width="90" show-overflow-tooltip />
          <el-table-column label="操作" width="120" class-name="no-print">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="openBonus(row)">设置奖金</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="shrink-0 flex justify-end px-4 md:px-6 py-3 border-t border-white/8">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 30, 50, 100]"
          :total="records.length"
          layout="total, sizes, prev, pager, next"
          background
          small
        />
      </div>
    </div>

    <el-dialog v-model="bonusVisible" title="设置奖金" width="400px">
      <el-form :model="bonusForm" label-width="80px">
        <el-form-item label="员工">{{ bonusForm.employee_name }}</el-form-item>
        <el-form-item label="奖金金额"><el-input-number v-model="bonusForm.bonus" :precision="2" :min="0" /></el-form-item>
        <el-form-item label="奖金备注"><el-input v-model="bonusForm.bonus_remark" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bonusVisible = false">取消</el-button>
        <el-button type="primary" @click="saveBonus">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { salaryApi } from '@/api'
import { useTableHeight } from '@/composables/useTableHeight'
import * as XLSX from 'xlsx'

const loading = ref(false)
const generating = ref(false)
const records = ref([])
const yearMonth = ref(new Date().toISOString().slice(0, 7))
const currentPage = ref(1)
const pageSize = ref(30)
const pagedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return records.value.slice(start, start + pageSize.value)
})
const tableBodyRef = ref(null)
const tableHeight = useTableHeight(tableBodyRef)
const bonusVisible = ref(false)
const bonusForm = reactive({ employee_id: null, year_month: '', bonus: 0, bonus_remark: '', employee_name: '' })

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const res = await salaryApi.list({ year_month: yearMonth.value })
    records.value = res.data
    currentPage.value = 1
  } finally { loading.value = false }
}

async function generateSalary() {
  generating.value = true
  try {
    const res = await salaryApi.generate(yearMonth.value)
    ElMessage.success(res.data.message)
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '生成失败') }
  finally { generating.value = false }
}

function openBonus(row) {
  Object.assign(bonusForm, { employee_id: row.employee_id, year_month: row.year_month, bonus: Number(row.bonus), bonus_remark: row.bonus_remark || '', employee_name: row.employee_name })
  bonusVisible.value = true
}

async function saveBonus() {
  try {
    await salaryApi.setBonus({ employee_id: bonusForm.employee_id, year_month: bonusForm.year_month, bonus: bonusForm.bonus, bonus_remark: bonusForm.bonus_remark })
    ElMessage.success('奖金设置成功')
    bonusVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '设置失败') }
}

function fmtMoney(_, __, val) { return val ? `¥${Number(val).toFixed(2)}` : '¥0.00' }

function exportExcel() {
  const data = records.value.map(r => ({
    员工: r.employee_name, 部门: r.department_name, 级别: r.level_name,
    年月: r.year_month, 基本工资: r.base_salary, 奖金: r.bonus,
    罚款: r.penalty, 实发工资: r.total_salary, 奖金备注: r.bonus_remark,
  }))
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '工资单')
  XLSX.writeFile(wb, `工资单_${yearMonth.value}.xlsx`)
}

function printTable() { window.print() }
</script>

<style>
@media print {
  .no-print, .el-header, .el-aside, .el-card__header .el-button { display: none !important; }
}
</style>
