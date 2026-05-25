<template>
  <div class="space-y-4 md:space-y-6">
    <div>
      <h1 class="font-serif font-semibold text-xl md:text-2xl text-white/95">我的信息</h1>
    </div>

    <div class="bg-[#2c2c2e] border border-white/8 rounded-xl overflow-hidden">
      <div class="px-4 md:px-6 py-3 border-b border-white/8">
        <h2 class="font-semibold text-sm text-white/90">个人档案</h2>
      </div>
      <div class="p-4 md:p-6">
        <div v-if="emp" class="grid grid-cols-1 sm:grid-cols-2 gap-0 border border-white/8 rounded-xl overflow-hidden">
          <div v-for="(item, i) in profileFields" :key="i"
               class="flex items-start gap-4 px-5 py-3.5 border-b border-white/8 last:border-b-0 sm:odd:border-r sm:odd:border-white/8">
            <span class="w-20 flex-shrink-0 text-xs text-white/45 font-medium pt-0.5">{{ item.label }}</span>
            <span class="text-sm text-white/88 flex-1">{{ item.value }}</span>
          </div>
        </div>
        <div v-else class="text-sm text-white/35 text-center py-8">暂无员工档案信息</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { employeeApi } from '@/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const emp = ref(null)

onMounted(async () => {
  if (auth.employeeId) {
    emp.value = (await employeeApi.get(auth.employeeId)).data
  }
})

function statusLabel(s) { return { active: '在职', transferred: '调动', resigned: '离职' }[s] || s }

const profileFields = computed(() => {
  if (!emp.value) return []
  return [
    { label: '姓名', value: emp.value.name },
    { label: '性别', value: emp.value.gender },
    { label: '身份证号', value: emp.value.id_card },
    { label: '联系电话', value: emp.value.phone },
    { label: '邮箱', value: emp.value.email || '-' },
    { label: '所在部门', value: emp.value.department_name },
    { label: '员工级别', value: emp.value.level_name },
    { label: '基本工资', value: `¥${Number(emp.value.base_salary).toFixed(2)}` },
    { label: '入职日期', value: emp.value.hire_date },
    { label: '状态', value: statusLabel(emp.value.status) },
  ]
})
</script>
