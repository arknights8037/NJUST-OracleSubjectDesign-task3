<template>
  <div class="h-full flex flex-col gap-3 md:gap-4">
    <!-- 筛选栏 -->
    <div class="shrink-0 bg-[#2c2c2e] border border-white/8 rounded-xl p-3 md:px-4">
      <div class="flex flex-wrap gap-3 items-end">
        <div class="flex-1 min-w-[160px]">
          <p class="text-xs text-white/45 mb-1.5">员工姓名</p>
          <el-input v-model="filter.keyword" placeholder="搜索员工姓名…" clearable @keyup.enter="handleSearch">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
        <div>
          <p class="text-xs text-white/45 mb-1.5">部门</p>
          <el-select v-model="filter.department_id" clearable placeholder="全部部门" style="width:150px">
            <el-option v-for="d in depts" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </div>
        <div>
          <p class="text-xs text-white/45 mb-1.5">变动类型</p>
          <el-select v-model="filter.change_type" clearable placeholder="全部类型" style="width:130px">
            <el-option label="入职" value="hire" />
            <el-option label="调动" value="transfer" />
            <el-option label="离职" value="resign" />
            <el-option label="级别变更" value="level_change" />
            <el-option label="工资变更" value="salary_change" />
          </el-select>
        </div>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilter">重置</el-button>
      </div>
    </div>

    <!-- 表格卡片 -->
    <div class="flex-1 min-h-0 flex flex-col bg-[#2c2c2e] border border-white/8 rounded-xl overflow-hidden">
      <div ref="tableBodyRef" class="flex-1 min-h-0">
        <el-table :data="pagedHistory" border v-loading="loading" :height="tableHeight" style="width:100%">
          <el-table-column prop="employee_name" label="员工" min-width="80" sortable />
          <el-table-column prop="change_type" label="变动类型" min-width="85" sortable>
            <template #default="{ row }">
              <el-tag :type="typeTag(row.change_type)">{{ typeLabel(row.change_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="old_department_name" label="原部门" min-width="80" sortable show-overflow-tooltip />
          <el-table-column prop="new_department_name" label="新部门" min-width="80" sortable show-overflow-tooltip />
          <el-table-column prop="old_level_name" label="原级别" min-width="80" sortable show-overflow-tooltip />
          <el-table-column prop="new_level_name" label="新级别" min-width="80" sortable show-overflow-tooltip />
          <el-table-column prop="old_base_salary" label="原工资" min-width="90" sortable :formatter="fmtMoney" />
          <el-table-column prop="new_base_salary" label="新工资" min-width="90" sortable :formatter="fmtMoney" />
          <el-table-column prop="remark" label="备注" min-width="80" show-overflow-tooltip />
          <el-table-column prop="operator_name" label="操作人" min-width="80" sortable />
          <el-table-column prop="operated_at" label="操作时间" min-width="150" sortable />
        </el-table>
      </div>
      <div class="shrink-0 flex justify-end px-4 md:px-6 py-3 border-t border-white/8">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 30, 50, 100]"
          :total="filteredHistory.length"
          layout="total, sizes, prev, pager, next"
          background
          small
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { employeeApi, deptApi } from '@/api'
import { useTableHeight } from '@/composables/useTableHeight'

const loading = ref(false)
const history = ref([])
const depts = ref([])
const filter = ref({ keyword: '', department_id: null, change_type: null })
const currentPage = ref(1)
const pageSize = ref(30)
const tableBodyRef = ref(null)
const tableHeight = useTableHeight(tableBodyRef)

onMounted(async () => {
  const [, deptRes] = await Promise.all([loadData(), deptApi.list()])
  depts.value = deptRes.data
})

async function loadData() {
  loading.value = true
  try {
    history.value = (await employeeApi.allHistory({})).data
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
}

function resetFilter() {
  filter.value = { keyword: '', department_id: null, change_type: null }
  currentPage.value = 1
}

// 部门 id → 名称映射
const deptNameMap = computed(() => {
  const m = {}
  depts.value.forEach(d => { m[d.id] = d.name })
  return m
})

const filteredHistory = computed(() => {
  let result = history.value
  const kw = filter.value.keyword?.trim().toLowerCase()
  if (kw) {
    result = result.filter(r => r.employee_name?.toLowerCase().includes(kw))
  }
  if (filter.value.department_id) {
    const name = deptNameMap.value[filter.value.department_id]
    if (name) {
      result = result.filter(r =>
        r.new_department_name === name || r.old_department_name === name
      )
    }
  }
  if (filter.value.change_type) {
    result = result.filter(r => r.change_type === filter.value.change_type)
  }
  return result
})

// 筛选条件变化时重置到第 1 页
watch(filter, () => { currentPage.value = 1 }, { deep: true })

const pagedHistory = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredHistory.value.slice(start, start + pageSize.value)
})

function typeLabel(t) {
  return { hire: '入职', transfer: '调动', resign: '离职', level_change: '级别变更', salary_change: '工资变更' }[t] || t
}
function typeTag(t) {
  return { hire: 'success', transfer: 'primary', resign: 'danger', level_change: 'warning', salary_change: 'info' }[t] || ''
}
function fmtMoney(_, __, val) { return val ? `¥${Number(val).toFixed(2)}` : '-' }
</script>

