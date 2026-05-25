<template>
  <div class="h-full flex flex-col">
    <!-- 表格卡片 -->
    <div class="flex-1 min-h-0 flex flex-col bg-[#2c2c2e] border border-white/8 rounded-xl overflow-hidden">
      <div class="shrink-0 flex flex-wrap items-center gap-3 px-4 md:px-6 py-3 border-b border-white/8">
        <h2 class="font-semibold text-sm text-white/90 mr-auto">考勤记录</h2>
        <el-date-picker v-model="dateRange" type="daterange" value-format="YYYY-MM-DD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width:280px" />
        <el-button type="primary" size="small" @click="loadData">查询</el-button>
      </div>
      <div ref="tableBodyRef" class="flex-1 min-h-0">
        <el-table :data="pagedRecords" border v-loading="loading" :height="tableHeight" style="width:100%">
          <el-table-column prop="employee_name" label="员工" min-width="80" sortable />
          <el-table-column prop="attend_date" label="日期" min-width="100" sortable />
          <el-table-column prop="check_in" label="签到" min-width="150" :formatter="fmtDt" sortable />
          <el-table-column prop="check_out" label="签离" min-width="150" :formatter="fmtDt" sortable />
          <el-table-column prop="status" label="当前状态" min-width="75" sortable>
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="late_minutes" label="迟到(分)" min-width="75" sortable />
          <el-table-column prop="penalty_amount" label="罚款" :formatter="fmtMoney" min-width="75" sortable />
          <el-table-column label="操作" width="210">
            <template #default="{ row }">
              <div class="flex items-center gap-2">
                <el-select v-model="confirmStatus[row.id]" size="small" style="min-width:110px;flex:1">
                  <el-option label="正常" value="normal" />
                  <el-option label="迟到" value="late" />
                  <el-option label="出差" value="business_trip" />
                  <el-option label="外出" value="outside" />
                  <el-option label="缺勤" value="absent" />
                </el-select>
                <el-button size="small" type="primary" @click="doConfirm(row)">确认</el-button>
              </div>
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
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { attendanceApi } from '@/api'
import { useTableHeight } from '@/composables/useTableHeight'

const loading = ref(false)
const records = ref([])
const dateRange = ref([])
const confirmStatus = reactive({})
const currentPage = ref(1)
const pageSize = ref(30)
const tableBodyRef = ref(null)
const tableHeight = useTableHeight(tableBodyRef)

loadData()

async function loadData() {
  loading.value = true
  currentPage.value = 1
  try {
    const params = {}
    if (dateRange.value?.length === 2) { params.start_date = dateRange.value[0]; params.end_date = dateRange.value[1] }
    const res = await attendanceApi.list(params)
    records.value = res.data
    res.data.forEach(r => { if (!confirmStatus[r.id]) confirmStatus[r.id] = r.status })
  } finally { loading.value = false }
}

const pagedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return records.value.slice(start, start + pageSize.value)
})

async function doConfirm(row) {
  try {
    await attendanceApi.confirm(row.id, { status: confirmStatus[row.id] })
    ElMessage.success('确认成功')
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') }
}

function fmtDt(_, __, val) { return val ? new Date(val).toLocaleString('zh-CN') : '-' }
function fmtMoney(_, __, val) { return val ? `¥${Number(val).toFixed(2)}` : '-' }
function statusLabel(s) { return { normal: '正常', late: '迟到', absent: '缺勤', business_trip: '出差', outside: '外出' }[s] || s }
function statusType(s) { return { normal: 'success', late: 'warning', absent: 'danger', business_trip: 'info', outside: '' }[s] || '' }
</script>

