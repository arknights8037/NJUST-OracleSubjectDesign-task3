<template>
  <div class="h-full flex flex-col">
    <!-- 表格卡片 -->
    <div class="flex-1 min-h-0 flex flex-col bg-[#2c2c2e] border border-white/8 rounded-xl overflow-hidden">
      <div ref="tableBodyRef" class="flex-1 min-h-0">
        <el-table :data="configs" border v-loading="loading" :height="tableHeight" style="width:100%">
          <el-table-column prop="config_key" label="配置键" min-width="130" sortable />
          <el-table-column prop="config_name" label="名称" min-width="100" sortable />
          <el-table-column prop="amount" label="金额(元)" min-width="90" sortable :formatter="fmtMoney" />
          <el-table-column prop="description" label="说明" min-width="100" show-overflow-tooltip />
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button size="small" @click="openEdit(row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" title="编辑罚款配置" width="400px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="名称">{{ form.config_name }}</el-form-item>
        <el-form-item label="罚款金额"><el-input-number v-model="form.amount" :precision="2" :min="0" /></el-form-item>
        <el-form-item label="说明"><el-input v-model="form.description" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { penaltyApi } from '@/api'
import { useTableHeight } from '@/composables/useTableHeight'

const loading = ref(false)
const configs = ref([])
const dialogVisible = ref(false)
const editId = ref(null)
const form = reactive({ config_name: '', amount: 0, description: '' })
const tableBodyRef = ref(null)
const tableHeight = useTableHeight(tableBodyRef)

onMounted(loadData)
async function loadData() {
  loading.value = true
  try { configs.value = (await penaltyApi.list()).data } finally { loading.value = false }
}
function openEdit(row) { editId.value = row.id; form.config_name = row.config_name; form.amount = Number(row.amount); form.description = row.description; dialogVisible.value = true }
async function save() {
  try { await penaltyApi.update(editId.value, { amount: form.amount, description: form.description }); ElMessage.success('保存成功'); dialogVisible.value = false; loadData() }
  catch (e) { ElMessage.error(e.response?.data?.detail || '保存失败') }
}
function fmtMoney(_, __, val) { return val ? `¥${Number(val).toFixed(2)}` : '-' }
</script>
