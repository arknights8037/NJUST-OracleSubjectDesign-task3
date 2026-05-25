<template>
  <div class="h-full flex flex-col gap-3 md:gap-4">
    <!-- 筛选栏 -->
    <div class="shrink-0 bg-[#2c2c2e] border border-white/8 rounded-xl p-3 md:p-4">
      <div class="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div class="grid flex-1 grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <div>
            <p class="text-xs text-white/45 mb-1.5">姓名</p>
            <el-input v-model="filter.name" placeholder="搜索姓名" clearable class="w-full" />
          </div>
          <div>
            <p class="text-xs text-white/45 mb-1.5">部门</p>
            <el-select v-model="filter.department_id" clearable placeholder="全部" class="w-full">
              <el-option v-for="d in depts" :key="d.id" :label="d.name" :value="d.id" />
            </el-select>
          </div>
          <div>
            <p class="text-xs text-white/45 mb-1.5">状态</p>
            <el-select v-model="filter.status" clearable placeholder="全部" class="w-full">
              <el-option label="在职" value="active" />
              <el-option label="调动" value="transferred" />
              <el-option label="离职" value="resigned" />
            </el-select>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-2 xl:justify-end">
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
          <el-button type="success" @click="openCreate">新增员工</el-button>
        </div>
      </div>
    </div>

    <!-- 表格卡片 -->
    <div class="flex-1 min-h-0 flex flex-col bg-[#2c2c2e] border border-white/8 rounded-xl overflow-hidden">
      <div ref="tableBodyRef" class="flex-1 min-h-0">
        <el-table :data="pagedEmployees" border v-loading="loading" :height="tableHeight" style="width:100%">
          <el-table-column prop="name" label="姓名" min-width="90" sortable />
          <el-table-column prop="gender" label="性别" width="55" sortable />
          <el-table-column prop="department_name" label="部门" min-width="90" sortable show-overflow-tooltip />
          <el-table-column prop="level_name" label="级别" min-width="80" sortable show-overflow-tooltip />
          <el-table-column prop="base_salary" label="基本工资" min-width="95" sortable :formatter="fmtMoney" />
          <el-table-column prop="hire_date" label="入职日期" min-width="100" sortable />
          <el-table-column prop="username" label="账号" min-width="100" sortable show-overflow-tooltip />
          <el-table-column prop="status" label="状态" min-width="65" sortable>
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="250" align="right">
            <template #default="{ row }">
              <div class="flex flex-wrap justify-end gap-1.5 employee-actions">
                <el-button size="small" @click="openEdit(row)">编辑</el-button>
                <el-button size="small" type="warning" @click="openTransfer(row)" :disabled="row.status !== 'active'">调动</el-button>
                <el-button size="small" type="danger" @click="openResign(row)" :disabled="row.status !== 'active'">离职</el-button>
                <el-button size="small" type="info" @click="viewHistory(row)">历史</el-button>
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
          :total="employees.length"
          layout="total, sizes, prev, pager, next"
          background
          small
        />
      </div>
    </div>

    <!-- 新增/编辑员工弹窗 -->
    <el-dialog v-model="createVisible" :title="editMode ? '编辑员工' : '新增员工'" width="600px">
      <el-form :model="empForm" :rules="empRules" ref="empFormRef" label-width="90px">
        <el-form-item label="姓名" prop="name"><el-input v-model="empForm.name" :disabled="editMode && !fieldEditing" class="w-full" /></el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="empForm.gender" :disabled="editMode && !fieldEditing">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="身份证号" prop="id_card"><el-input v-model="empForm.id_card" :disabled="editMode" class="w-full" /></el-form-item>
        <el-form-item label="联系电话" prop="phone"><el-input v-model="empForm.phone" :disabled="editMode && !fieldEditing" class="w-full" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="empForm.email" :disabled="editMode && !fieldEditing" class="w-full" /></el-form-item>
        <el-form-item label="部门" prop="department_id">
          <el-select v-model="empForm.department_id" :disabled="editMode && !fieldEditing" class="w-full">
            <el-option v-for="d in depts" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="级别" prop="level_id">
          <el-select v-model="empForm.level_id" :disabled="editMode && !fieldEditing" class="w-full">
            <el-option v-for="l in levels" :key="l.id" :label="l.level_name" :value="l.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="入职日期" prop="hire_date">
          <el-date-picker v-model="empForm.hire_date" type="date" value-format="YYYY-MM-DD" :disabled="editMode && !fieldEditing" class="w-full" />
        </el-form-item>
        <template v-if="!editMode">
          <el-form-item label="登录账号" prop="username"><el-input v-model="empForm.username" class="w-full" /></el-form-item>
          <el-form-item label="初始密码" prop="password"><el-input v-model="empForm.password" type="password" show-password class="w-full" /></el-form-item>
          <el-form-item label="角色" prop="role">
            <el-select v-model="empForm.role" class="w-full">
              <el-option label="普通员工" value="employee" />
              <el-option label="部门经理" value="manager" />
              <el-option label="管理员" value="admin" />
            </el-select>
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button v-if="editMode && !fieldEditing" type="primary" @click="fieldEditing = true">编辑</el-button>
        <el-button v-if="!editMode || fieldEditing" type="primary" :loading="saving" @click="saveEmployee">保存</el-button>
      </template>
    </el-dialog>

    <!-- 调动弹窗 -->
    <el-dialog v-model="transferVisible" title="员工调动" width="420px">
      <el-form :model="transferForm" label-width="90px">
        <el-form-item label="新部门">
          <el-select v-model="transferForm.new_department_id" clearable class="w-full">
            <el-option v-for="d in depts" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="新级别">
          <el-select v-model="transferForm.new_level_id" clearable class="w-full">
            <el-option v-for="l in levels" :key="l.id" :label="l.level_name" :value="l.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="transferForm.remark" class="w-full" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="transferVisible = false">取消</el-button>
        <el-button type="primary" @click="doTransfer">确认调动</el-button>
      </template>
    </el-dialog>

    <!-- 离职弹窗 -->
    <el-dialog v-model="resignVisible" title="员工离职" width="420px">
      <el-form :model="resignForm" label-width="90px">
        <el-form-item label="离职日期">
          <el-date-picker v-model="resignForm.resign_date" type="date" value-format="YYYY-MM-DD" class="w-full" />
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="resignForm.remark" class="w-full" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resignVisible = false">取消</el-button>
        <el-button type="danger" @click="doResign">确认离职</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { employeeApi, deptApi, levelApi } from '@/api'
import { useTableHeight } from '@/composables/useTableHeight'

const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const employees = ref([])
const currentPage = ref(1)
const pageSize = ref(30)
const pagedEmployees = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return employees.value.slice(start, start + pageSize.value)
})
const tableBodyRef = ref(null)
const tableHeight = useTableHeight(tableBodyRef)
const depts = ref([])
const levels = ref([])

const filter = reactive({ name: '', department_id: null, status: null })
const createVisible = ref(false)
const editMode = ref(false)
const fieldEditing = ref(false)
const currentEmpId = ref(null)
const empFormRef = ref()
const empForm = reactive({
  name: '', gender: '男', id_card: '', phone: '', email: '',
  department_id: null, level_id: null, hire_date: '',
  username: '', password: '', role: 'employee',
})
const empRules = {
  name: [{ required: true, message: '请输入姓名' }],
  id_card: [{ required: true, message: '请输入身份证号' }],
  department_id: [{ required: true, message: '请选择部门' }],
  level_id: [{ required: true, message: '请选择级别' }],
  hire_date: [{ required: true, message: '请选择入职日期' }],
  username: [{ required: true, message: '请输入账号' }],
  password: [{ required: true, message: '请输入密码' }],
}

const transferVisible = ref(false)
const transferForm = reactive({ new_department_id: null, new_level_id: null, remark: '' })
const resignVisible = ref(false)
const resignForm = reactive({ resign_date: new Date().toISOString().slice(0, 10), remark: '' })
let activeEmpId = null

onMounted(async () => {
  const [d, l] = await Promise.all([deptApi.list(), levelApi.list()])
  depts.value = d.data
  levels.value = l.data
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const params = {}
    if (filter.name) params.name = filter.name
    if (filter.department_id) params.department_id = filter.department_id
    if (filter.status) params.status = filter.status
    const res = await employeeApi.list(params)
    employees.value = res.data
    currentPage.value = 1
  } finally {
    loading.value = false
  }
}

function resetFilter() {
  filter.name = ''; filter.department_id = null; filter.status = null
  loadData()
}

function fmtMoney(row, col, val) {
  return val ? `¥${Number(val).toFixed(2)}` : '-'
}
function statusType(s) { return { active: 'success', transferred: 'warning', resigned: 'danger' }[s] || '' }
function statusLabel(s) { return { active: '在职', transferred: '调动', resigned: '离职' }[s] || s }

function openCreate() {
  editMode.value = false
  Object.assign(empForm, { name: '', gender: '男', id_card: '', phone: '', email: '', department_id: null, level_id: null, hire_date: '', username: '', password: '', role: 'employee' })
  createVisible.value = true
}
function openEdit(row) {
  editMode.value = true
  fieldEditing.value = false
  currentEmpId.value = row.id
  Object.assign(empForm, {
    name: row.name, gender: row.gender, id_card: row.id_card,
    phone: row.phone, email: row.email,
    department_id: row.department_id, level_id: row.level_id, hire_date: row.hire_date,
  })
  createVisible.value = true
}

async function saveEmployee() {
  await empFormRef.value.validate()
  saving.value = true
  try {
    if (editMode.value) {
      await employeeApi.update(currentEmpId.value, { name: empForm.name, gender: empForm.gender, phone: empForm.phone, email: empForm.email, department_id: empForm.department_id, level_id: empForm.level_id, hire_date: empForm.hire_date })
    } else {
      await employeeApi.create({ ...empForm })
    }
    ElMessage.success('保存成功')
    createVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

function openTransfer(row) {
  activeEmpId = row.id
  Object.assign(transferForm, { new_department_id: row.department_id, new_level_id: row.level_id, remark: '' })
  transferVisible.value = true
}
async function doTransfer() {
  try {
    await employeeApi.transfer(activeEmpId, transferForm)
    ElMessage.success('调动成功')
    transferVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') }
}

function openResign(row) {
  activeEmpId = row.id
  resignForm.remark = ''
  resignVisible.value = true
}
async function doResign() {
  try {
    await employeeApi.resign(activeEmpId, resignForm)
    ElMessage.success('办理离职成功')
    resignVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') }
}

function viewHistory(row) {
  router.push(`/admin/employees/${row.id}/history`)
}
</script>

<style scoped>
.employee-actions :deep(.el-button) {
  margin-left: 0;
}

.employee-action-btn {
  min-width: 58px;
  justify-content: center;
}
</style>
