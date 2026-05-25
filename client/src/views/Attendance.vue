<template>
  <div class="space-y-4 md:space-y-6">

    <!-- 标题 -->
    <div>
      <h1 class="font-serif font-semibold text-xl md:text-2xl text-white/95">考勤打卡</h1>
      <p class="text-xs text-white/40 mt-0.5">{{ currentTime }}</p>
    </div>

    <!-- 打卡操作区 -->
    <div class="bg-[#2c2c2e] border border-white/8 rounded-xl p-4 md:p-6">
      <div class="flex flex-wrap gap-3">
        <button
          @click="checkIn"
          :disabled="checking"
          class="flex items-center gap-2 px-5 py-3 bg-[#1a5c2a] border border-[rgba(50,215,75,0.30)] rounded-lg text-[#32d74b] text-sm font-semibold transition-colors duration-200 hover:bg-[#1f6e33] active:opacity-80 disabled:opacity-50"
        >
          <el-icon><Check /></el-icon>
          签 到
        </button>
        <button
          @click="checkOut"
          :disabled="checking"
          class="flex items-center gap-2 px-5 py-3 bg-[#4a3800] border border-[rgba(255,214,10,0.30)] rounded-lg text-[#ffd60a] text-sm font-semibold transition-colors duration-200 hover:bg-[#5a4500] active:opacity-80 disabled:opacity-50"
        >
          <el-icon><Close /></el-icon>
          签 离
        </button>
      </div>
    </div>

    <!-- 考勤记录 -->
    <div class="bg-[#2c2c2e] border border-white/8 rounded-xl overflow-hidden">
      <div class="flex flex-wrap items-center gap-3 px-4 md:px-6 py-3 border-b border-white/8">
        <h2 class="font-semibold text-sm text-white/90 mr-auto">考勤记录</h2>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          value-format="YYYY-MM-DD"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width:280px"
        />
        <el-button type="primary" size="small" @click="loadData">查询</el-button>
      </div>
      <div class="p-4 md:p-6">
        <el-table :data="records" stripe v-loading="loading" style="width:100%">
          <el-table-column prop="attend_date" label="日期" width="110" sortable />
          <el-table-column prop="check_in" label="签到时间" width="170" :formatter="fmtDt" sortable />
          <el-table-column prop="check_out" label="签离时间" width="170" :formatter="fmtDt" sortable />
          <el-table-column prop="status" label="状态" width="90" sortable>
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="late_minutes" label="迟到(分钟)" width="100" sortable />
          <el-table-column prop="penalty_amount" label="罚款" :formatter="fmtMoney" width="90" sortable />
          <el-table-column prop="remark" label="备注" />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { attendanceApi } from '@/api'

const loading = ref(false)
const checking = ref(false)
const records = ref([])
const dateRange = ref([])

let timer = null
const currentTime = ref(new Date().toLocaleString('zh-CN'))

onMounted(() => {
  timer = setInterval(() => { currentTime.value = new Date().toLocaleString('zh-CN') }, 1000)
  loadData()
})
onUnmounted(() => clearInterval(timer))

async function loadData() {
  loading.value = true
  try {
    const params = {}
    if (dateRange.value?.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const res = await attendanceApi.list(params)
    records.value = res.data
  } finally {
    loading.value = false
  }
}

async function checkIn() {
  checking.value = true
  try {
    await attendanceApi.checkIn({})
    ElMessage.success('签到成功')
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '签到失败') }
  finally { checking.value = false }
}

async function checkOut() {
  checking.value = true
  try {
    await attendanceApi.checkOut({})
    ElMessage.success('签离成功')
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '签离失败') }
  finally { checking.value = false }
}

function fmtDt(_, __, val) { return val ? new Date(val).toLocaleString('zh-CN') : '-' }
function fmtMoney(_, __, val) { return val ? `¥${Number(val).toFixed(2)}` : '-' }
function statusLabel(s) { return { normal: '正常', late: '迟到', absent: '缺勤', business_trip: '出差', outside: '外出' }[s] || s }
function statusType(s) { return { normal: 'success', late: 'warning', absent: 'danger', business_trip: 'info', outside: '' }[s] || '' }
</script>
