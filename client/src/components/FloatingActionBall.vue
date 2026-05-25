<template>
  <div class="fab-root">
    <transition name="fab-actions">
      <div v-if="expanded" class="fab-panel">
        <button class="fab-panel-action" @click="openSeedDialog">
          <span class="fab-panel-icon">
            <el-icon><Files /></el-icon>
          </span>
          <span>
            <strong>批量写入测试数据</strong>
            <small>快速生成员工、考勤和工资测试记录</small>
          </span>
        </button>
      </div>
    </transition>

    <button class="fab-button" :class="expanded ? 'is-expanded' : ''" @click="expanded = !expanded">
      <el-icon class="fab-button-icon"><component :is="expanded ? 'CloseBold' : 'Operation'" /></el-icon>
      <span class="fab-button-text">系统操作</span>
    </button>

    <el-dialog v-model="dialogVisible" title="批量写入测试数据" width="480px">
      <el-form label-width="110px" class="fab-form">
        <el-form-item label="员工数量">
          <el-input-number v-model="form.employee_count" :min="1" :max="100" class="w-full" />
        </el-form-item>
        <el-form-item label="目标月份">
          <el-date-picker v-model="form.year_month" type="month" value-format="YYYY-MM" class="w-full" />
        </el-form-item>
        <el-form-item label="生成考勤">
          <el-switch v-model="form.include_attendance" />
        </el-form-item>
        <el-form-item label="生成工资">
          <el-switch v-model="form.generate_salary" :disabled="!form.include_attendance" />
        </el-form-item>
      </el-form>

      <div class="fab-tip">
        默认会创建测试员工账号，初始密码固定为 test123456。
      </div>

      <div v-if="result" class="fab-result">
        <p>已写入 {{ result.employee_count }} 名员工，{{ result.attendance_count }} 条考勤，{{ result.salary_count }} 条工资记录。</p>
        <p>数据月份：{{ result.year_month }}</p>
        <p>默认密码：{{ result.initial_password }}</p>
        <p class="fab-result-users">账号示例：{{ result.usernames.slice(0, 4).join('、') }}<span v-if="result.usernames.length > 4"> 等</span></p>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
        <el-button type="primary" :loading="loading" @click="submitSeed">开始写入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { employeeApi } from '@/api'

const expanded = ref(false)
const dialogVisible = ref(false)
const loading = ref(false)
const result = ref(null)
const form = reactive({
  employee_count: 12,
  year_month: new Date().toISOString().slice(0, 7),
  include_attendance: true,
  generate_salary: true,
})

function openSeedDialog() {
  expanded.value = false
  dialogVisible.value = true
}

async function submitSeed() {
  loading.value = true
  try {
    const payload = {
      employee_count: form.employee_count,
      year_month: form.year_month,
      include_attendance: form.include_attendance,
      generate_salary: form.include_attendance && form.generate_salary,
    }
    const { data } = await employeeApi.seedTestData(payload)
    result.value = data
    ElMessage.success('测试数据写入完成')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '写入测试数据失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fab-root {
  position: fixed;
  right: 28px;
  bottom: 28px;
  z-index: 80;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.fab-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 999px;
  border: 1px solid rgba(107, 114, 255, 0.28);
  background: linear-gradient(135deg, rgba(107, 114, 255, 0.92), rgba(86, 95, 227, 0.92));
  color: #fff;
  box-shadow: 0 16px 36px rgba(32, 37, 86, 0.35);
  backdrop-filter: blur(18px);
}

.fab-button.is-expanded {
  box-shadow: 0 20px 44px rgba(32, 37, 86, 0.42);
}

.fab-button-icon {
  font-size: 18px;
}

.fab-button-text {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.fab-panel {
  width: min(360px, calc(100vw - 32px));
  padding: 10px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(44, 44, 46, 0.94);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(18px);
}

.fab-panel-action {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px;
  border-radius: 14px;
  color: rgba(255, 255, 255, 0.92);
  transition: background-color 180ms ease, transform 180ms ease;
}

.fab-panel-action:hover {
  background: rgba(107, 114, 255, 0.14);
  transform: translateY(-1px);
}

.fab-panel-icon {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: rgba(107, 114, 255, 0.18);
  color: #c5c9ff;
  font-size: 18px;
}

.fab-panel-action strong,
.fab-panel-action small {
  display: block;
}

.fab-panel-action strong {
  font-size: 13px;
  font-weight: 600;
}

.fab-panel-action small {
  margin-top: 3px;
  color: rgba(255, 255, 255, 0.52);
  font-size: 12px;
}

.fab-tip {
  margin-top: 4px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(107, 114, 255, 0.1);
  color: rgba(255, 255, 255, 0.72);
  font-size: 12px;
}

.fab-result {
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.82);
  font-size: 12px;
  line-height: 1.7;
}

.fab-result p {
  margin: 0;
}

.fab-result-users {
  color: rgba(255, 255, 255, 0.6);
}

.fab-actions-enter-active,
.fab-actions-leave-active {
  transition: all 180ms ease;
}

.fab-actions-enter-from,
.fab-actions-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.96);
}

@media (max-width: 768px) {
  .fab-root {
    right: 16px;
    bottom: 18px;
  }

  .fab-button {
    padding: 12px;
  }

  .fab-button-text {
    display: none;
  }
}
</style>