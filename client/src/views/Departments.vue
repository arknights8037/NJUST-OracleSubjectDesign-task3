<template>
  <div class="h-full flex flex-col">
    <!-- 表格卡片 -->
    <div class="flex-1 min-h-0 flex flex-col bg-[#2c2c2e] border border-white/8 rounded-xl overflow-hidden">
      <!-- 工具栏 -->
      <div class="shrink-0 flex flex-wrap items-center gap-3 px-4 md:px-6 py-3 border-b border-white/8">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索部门名称…"
          clearable
          style="width:220px"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <span class="text-xs text-white/35 ml-1">共 {{ filteredDepts.length }} 个部门</span>
        <div class="ml-auto">
          <el-button type="primary" @click="openCreate">新增部门</el-button>
        </div>
      </div>
      <div ref="tableBodyRef" class="flex-1 min-h-0">
        <el-table :data="pagedDepts" border v-loading="loading" :height="tableHeight" style="width:100%">
          <el-table-column prop="id" label="ID" width="60" sortable />
          <el-table-column prop="name" label="部门名称" min-width="100" sortable />
          <el-table-column prop="description" label="描述" min-width="100" show-overflow-tooltip />
          <el-table-column prop="employee_count" label="在职人数" min-width="90" align="center" sortable>
            <template #default="{ row }">
              <span class="font-medium text-[#6b72ff]">{{ row.employee_count ?? '—' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" min-width="70" sortable>
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" align="right">
            <template #default="{ row }">
              <div class="flex justify-end gap-1.5">
                <el-button size="small" @click="openEdit(row)">编辑</el-button>
                <el-button v-if="row.is_active" size="small" type="danger" @click="toggleActive(row)">停用</el-button>
                <el-button v-else size="small" type="success" @click="toggleActive(row)">启用</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="shrink-0 flex justify-end px-4 md:px-6 py-3 border-t border-white/8">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 30, 50]"
          :total="filteredDepts.length"
          layout="total, sizes, prev, pager, next"
          background
          small
        />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="editId ? '编辑部门' : '新增部门'" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="部门名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { deptApi, statsApi } from '@/api'
import { useTableHeight } from '@/composables/useTableHeight'

const loading = ref(false)
const rawDepts = ref([])
const headcount = ref([])
const dialogVisible = ref(false)
const editId = ref(null)
const form = reactive({ name: '', description: '' })
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(30)
const tableBodyRef = ref(null)
const tableHeight = useTableHeight(tableBodyRef)

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const [deptRes, hcRes] = await Promise.all([deptApi.list(), statsApi.deptHeadcount()])
    rawDepts.value = deptRes.data
    headcount.value = hcRes.data
  } finally { loading.value = false }
}

// 部门名 → 在职人数
const hcMap = computed(() => {
  const m = {}
  headcount.value.forEach(h => { m[h.department_name] = h.employee_count })
  return m
})

// 部门列表（附加人数字段）
const depts = computed(() =>
  rawDepts.value.map(d => ({ ...d, employee_count: hcMap.value[d.name] ?? 0 }))
)

const filteredDepts = computed(() => {
  const kw = searchKeyword.value.trim().toLowerCase()
  if (!kw) return depts.value
  return depts.value.filter(d => d.name.toLowerCase().includes(kw))
})

watch(searchKeyword, () => { currentPage.value = 1 })

const pagedDepts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredDepts.value.slice(start, start + pageSize.value)
})

function openCreate() { editId.value = null; form.name = ''; form.description = ''; dialogVisible.value = true }
function openEdit(row) { editId.value = row.id; form.name = row.name; form.description = row.description; dialogVisible.value = true }

async function save() {
  try {
    if (editId.value) await deptApi.update(editId.value, form)
    else await deptApi.create(form)
    ElMessage.success('保存成功'); dialogVisible.value = false; loadData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') }
}

async function toggleActive(row) {
  try {
    await deptApi.update(row.id, { is_active: !row.is_active })
    ElMessage.success(row.is_active ? '已停用' : '已启用')
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') }
}
</script>

