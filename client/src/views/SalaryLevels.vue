<template>
  <div class="h-full flex flex-col">
    <!-- 表格卡片 -->
    <div class="flex-1 min-h-0 flex flex-col bg-[#2c2c2e] border border-white/8 rounded-xl overflow-hidden">
      <div class="shrink-0 flex items-center justify-end px-4 md:px-6 py-3 border-b border-white/8">
        <el-button type="primary" @click="openCreate">新增级别</el-button>
      </div>
      <div ref="tableBodyRef" class="flex-1 min-h-0">
        <el-table :data="pagedLevels" border v-loading="loading" :height="tableHeight" style="width:100%">
          <el-table-column prop="level_code" label="代码" min-width="100" sortable />
          <el-table-column prop="level_name" label="级别名称" min-width="100" sortable />
          <el-table-column prop="base_salary" label="基本工资" min-width="100" sortable :formatter="fmtMoney" />
          <el-table-column prop="description" label="描述" min-width="100" show-overflow-tooltip />
          <el-table-column prop="sort_order" label="排序" min-width="65" />
          <el-table-column label="操作" width="150" align="right">
            <template #default="{ row }">
              <div class="flex justify-end gap-1.5">
                <el-button size="small" @click="openEdit(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
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
          :total="levels.length"
          layout="total, sizes, prev, pager, next"
          background
          small
        />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="editId ? '编辑级别' : '新增级别'" width="420px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="级别代码"><el-input v-model="form.level_code" :disabled="!!editId" /></el-form-item>
        <el-form-item label="级别名称"><el-input v-model="form.level_name" /></el-form-item>
        <el-form-item label="基本工资"><el-input-number v-model="form.base_salary" :precision="2" :min="0" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { levelApi } from '@/api'
import { useTableHeight } from '@/composables/useTableHeight'

const loading = ref(false)
const levels = ref([])
const currentPage = ref(1)
const pageSize = ref(30)
const pagedLevels = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return levels.value.slice(start, start + pageSize.value)
})
const tableBodyRef = ref(null)
const tableHeight = useTableHeight(tableBodyRef)
const dialogVisible = ref(false)
const editId = ref(null)
const form = reactive({ level_code: '', level_name: '', base_salary: 0, description: '', sort_order: 0 })

onMounted(loadData)
async function loadData() {
  loading.value = true
  try { levels.value = (await levelApi.list()).data } finally { loading.value = false }
}
function openCreate() { editId.value = null; Object.assign(form, { level_code: '', level_name: '', base_salary: 0, description: '', sort_order: 0 }); dialogVisible.value = true }
function openEdit(row) { editId.value = row.id; Object.assign(form, { level_code: row.level_code, level_name: row.level_name, base_salary: Number(row.base_salary), description: row.description, sort_order: row.sort_order }); dialogVisible.value = true }
async function save() {
  try {
    if (editId.value) await levelApi.update(editId.value, { level_name: form.level_name, base_salary: form.base_salary, description: form.description, sort_order: form.sort_order })
    else await levelApi.create(form)
    ElMessage.success('保存成功'); dialogVisible.value = false; loadData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') }
}
async function remove(row) {
  try { await levelApi.remove(row.id); ElMessage.success('已删除'); loadData() }
  catch (e) { ElMessage.error(e.response?.data?.detail || '删除失败') }
}
function fmtMoney(_, __, val) { return val ? `¥${Number(val).toFixed(2)}` : '-' }
</script>
