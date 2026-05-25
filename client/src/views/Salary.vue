<template>
  <div class="space-y-4 md:space-y-6">
    <div>
      <h1 class="font-serif font-semibold text-xl md:text-2xl text-white/95">我的工资</h1>
    </div>

    <div class="bg-[#2c2c2e] border border-white/8 rounded-xl overflow-hidden">
      <div class="px-4 md:px-6 py-3 border-b border-white/8">
        <h2 class="font-semibold text-sm text-white/90">工资记录</h2>
      </div>
      <div class="p-4 md:p-6">
        <el-table :data="records" stripe v-loading="loading" style="width:100%">
          <el-table-column prop="year_month" label="年月" width="90" sortable />
          <el-table-column prop="base_salary" label="基本工资" sortable :formatter="fmtMoney" />
          <el-table-column prop="bonus" label="奖金" sortable :formatter="fmtMoney" />
          <el-table-column prop="penalty" label="罚款" sortable :formatter="fmtMoney" />
          <el-table-column prop="total_salary" label="实发工资" sortable :formatter="fmtMoney">
            <template #default="{ row }">
              <span class="text-white/90 font-semibold">{{ fmtMoney(null, null, row.total_salary) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="bonus_remark" label="奖金备注" />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { salaryApi } from '@/api'

const loading = ref(false)
const records = ref([])
onMounted(async () => {
  loading.value = true
  try { records.value = (await salaryApi.my()).data } finally { loading.value = false }
})
function fmtMoney(_, __, val) { return val ? `¥${Number(val).toFixed(2)}` : '¥0.00' }
</script>
