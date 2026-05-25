<template>
  <el-dialog
    v-model="visible"
    :show-close="false"
    class="gs-dialog"
    width="540px"
    top="12vh"
    @closed="onClosed"
  >
    <!-- 搜索输入行 -->
    <div class="flex items-center gap-2.5 pb-3 border-b border-white/10">
      <el-icon class="shrink-0 text-white/35 text-base"><Search /></el-icon>
      <input
        ref="inputRef"
        v-model="keyword"
        class="flex-1 bg-transparent outline-none text-sm text-white/90 placeholder-white/30"
        placeholder="搜索员工、部门…"
        @keyup.esc="visible = false"
      />
      <kbd class="text-[10px] px-1.5 py-0.5 rounded bg-white/8 text-white/30 shrink-0">ESC</kbd>
    </div>

    <!-- 结果区 -->
    <div class="mt-2 max-h-72 overflow-y-auto">
      <!-- 加载中 -->
      <div v-if="bootstrapping" class="py-10 text-center text-white/30 text-sm">加载数据…</div>

      <!-- 无结果 -->
      <template v-else-if="keyword.trim() && results.length === 0">
        <div class="py-10 text-center text-white/30 text-sm">未找到匹配结果</div>
      </template>

      <!-- 默认提示 -->
      <template v-else-if="!keyword.trim()">
        <div class="py-10 text-center text-white/30 text-sm">输入关键词开始搜索</div>
      </template>

      <!-- 搜索结果 -->
      <template v-else>
        <!-- 员工结果 -->
        <template v-if="empResults.length">
          <p class="text-[11px] text-white/30 px-2 pt-1 pb-1">员工</p>
          <div
            v-for="emp in empResults"
            :key="'e' + emp.id"
            class="flex items-center gap-2.5 px-3 py-2 rounded-lg cursor-pointer hover:bg-white/6 transition-colors"
            @click="goEmployee"
          >
            <el-icon class="text-[#6b72ff] shrink-0"><User /></el-icon>
            <span class="text-white/90 text-sm font-medium">{{ emp.name }}</span>
            <span class="text-white/40 text-xs ml-0.5">{{ emp.department_name }}</span>
            <el-tag size="small" :type="empStatusType(emp.status)" class="ml-auto shrink-0">
              {{ empStatusLabel(emp.status) }}
            </el-tag>
          </div>
        </template>

        <!-- 部门结果 -->
        <template v-if="deptResults.length">
          <p class="text-[11px] text-white/30 px-2 pt-2 pb-1">部门</p>
          <div
            v-for="dept in deptResults"
            :key="'d' + dept.id"
            class="flex items-center gap-2.5 px-3 py-2 rounded-lg cursor-pointer hover:bg-white/6 transition-colors"
            @click="goDept"
          >
            <el-icon class="text-emerald-400 shrink-0"><OfficeBuilding /></el-icon>
            <span class="text-white/90 text-sm font-medium">{{ dept.name }}</span>
            <el-tag size="small" :type="dept.is_active ? 'success' : 'info'" class="ml-auto shrink-0">
              {{ dept.is_active ? '启用' : '停用' }}
            </el-tag>
          </div>
        </template>
      </template>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Search, User, OfficeBuilding } from '@element-plus/icons-vue'
import { employeeApi, deptApi } from '@/api'

const props = defineProps({ modelValue: { type: Boolean, default: false } })
const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: v => emit('update:modelValue', v),
})

const router = useRouter()
const keyword = ref('')
const bootstrapping = ref(false)
const employees = ref([])
const depts = ref([])
const inputRef = ref(null)

watch(visible, async v => {
  if (!v) return
  // 首次打开时拉取数据
  if (employees.value.length === 0 && depts.value.length === 0) {
    bootstrapping.value = true
    try {
      const [empRes, deptRes] = await Promise.all([employeeApi.list({}), deptApi.list()])
      employees.value = empRes.data
      depts.value = deptRes.data
    } finally {
      bootstrapping.value = false
    }
  }
  await nextTick()
  inputRef.value?.focus()
})

function onClosed() { keyword.value = '' }

const empResults = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return []
  return employees.value
    .filter(e => e.name?.toLowerCase().includes(kw) || e.department_name?.toLowerCase().includes(kw))
    .slice(0, 8)
})

const deptResults = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return []
  return depts.value.filter(d => d.name?.toLowerCase().includes(kw)).slice(0, 5)
})

const results = computed(() => [...empResults.value, ...deptResults.value])

function goEmployee() {
  visible.value = false
  router.push('/admin/employees')
}
function goDept() {
  visible.value = false
  router.push('/admin/departments')
}

function empStatusLabel(s) { return { active: '在职', transferred: '调动', resigned: '离职' }[s] || s }
function empStatusType(s) { return { active: 'success', transferred: 'warning', resigned: 'info' }[s] || '' }

// 全局 Ctrl+K 快捷键
function handleKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    visible.value = true
  }
}
onMounted(() => window.addEventListener('keydown', handleKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', handleKeydown))
</script>

<style>
/* 对话框整体背景覆盖（不用 scoped，避免深度选择器问题） */
.gs-dialog .el-dialog {
  background: #2c2c2e !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 14px !important;
}
.gs-dialog .el-dialog__header { display: none !important; }
.gs-dialog .el-dialog__body { padding: 18px 20px !important; }
</style>
