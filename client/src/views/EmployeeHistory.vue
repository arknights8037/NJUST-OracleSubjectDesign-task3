<template>
  <div class="space-y-4 md:space-y-6">
    <div class="flex items-center gap-3">
      <button
        @click="$router.back()"
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#3a3a3c] border border-white/10 text-white/60 text-xs hover:text-white/88 transition-colors duration-200"
      >
        <el-icon><ArrowLeft /></el-icon>
        返回
      </button>
      <span class="text-sm text-white/56">当前员工：{{ empName }}</span>
    </div>

    <div class="bg-[#2c2c2e] border border-white/8 rounded-xl overflow-hidden">
      <div class="p-4 md:p-6">
        <el-table :data="history" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="change_type" label="变动类型" width="100" sortable>
          <template #default="{ row }">
            <el-tag :type="typeTag(row.change_type)">{{ typeLabel(row.change_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="old_department_name" label="原部门" sortable />
        <el-table-column prop="new_department_name" label="新部门" sortable />
        <el-table-column prop="old_level_name" label="原级别" sortable />
        <el-table-column prop="new_level_name" label="新级别" sortable />
        <el-table-column prop="old_base_salary" label="原工资" sortable :formatter="fmtMoney" />
        <el-table-column prop="new_base_salary" label="新工资" sortable :formatter="fmtMoney" />
        <el-table-column prop="remark" label="备注" />
        <el-table-column prop="operator_name" label="操作人" width="90" sortable />
        <el-table-column prop="operated_at" label="操作时间" width="170" sortable />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { employeeApi } from '@/api'

const route = useRoute()
const loading = ref(false)
const history = ref([])
const empName = ref('')

onMounted(async () => {
  loading.value = true
  try {
    const empRes = await employeeApi.get(route.params.id)
    empName.value = empRes.data.name
    const res = await employeeApi.history(route.params.id)
    history.value = res.data
  } finally {
    loading.value = false
  }
})

function typeLabel(t) { return { hire: '入职', transfer: '调动', resign: '离职', level_change: '级别变更', salary_change: '工资变更' }[t] || t }
function typeTag(t) { return { hire: 'success', transfer: 'primary', resign: 'danger', level_change: 'warning', salary_change: 'info' }[t] || '' }
function fmtMoney(_, __, val) { return val ? `¥${Number(val).toFixed(2)}` : '-' }
</script>
