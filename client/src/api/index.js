/**
 * 前端 API 模块 - 封装所有后端接口调用
 *
 * 每个 api 对象对应一个后端路由模块，方法名与 HTTP 操作语义一致：
 *   list / get → GET   create → POST   update → PUT   remove → DELETE
 */
import http from './http'

/** 认证接口：用户登录 */
export const authApi = {
  /** POST /auth/login - 提交用户名和密码，返回 JWT 令牌及用户信息 */
  login: (data) => http.post('/auth/login', data),
}

/** 部门管理接口 */
export const deptApi = {
  /** GET /departments - 获取所有部门列表 */
  list: () => http.get('/departments'),
  /** POST /departments - 新建部门（需管理员权限） */
  create: (data) => http.post('/departments', data),
  /** PUT /departments/:id - 更新部门信息（需管理员权限） */
  update: (id, data) => http.put(`/departments/${id}`, data),
  /** DELETE /departments/:id - 停用部门（软删除，需管理员权限） */
  remove: (id) => http.delete(`/departments/${id}`),
}

/** 薪资等级接口 */
export const levelApi = {
  /** GET /salary-levels - 获取所有薪资等级（按排序升序） */
  list: () => http.get('/salary-levels'),
  /** POST /salary-levels - 新建薪资等级（需管理员权限） */
  create: (data) => http.post('/salary-levels', data),
  /** PUT /salary-levels/:id - 更新薪资等级（需管理员权限） */
  update: (id, data) => http.put(`/salary-levels/${id}`, data),
  /** DELETE /salary-levels/:id - 删除薪资等级（需管理员权限） */
  remove: (id) => http.delete(`/salary-levels/${id}`),
}

/** 罚款配置接口 */
export const penaltyApi = {
  /** GET /penalty-config - 获取迟到/缺勤罚款金额配置 */
  list: () => http.get('/penalty-config'),
  /** PUT /penalty-config/:id - 修改罚款金额（需管理员权限） */
  update: (id, data) => http.put(`/penalty-config/${id}`, data),
}

/** 员工档案接口 */
export const employeeApi = {
  /** GET /employees - 按条件筛选员工列表（支持姓名/部门/等级/状态/入职日期） */
  list: (params) => http.get('/employees', { params }),
  /** GET /employees/:id - 获取指定员工详情（普通员工只能查自己） */
  get: (id) => http.get(`/employees/${id}`),
  /** POST /employees - 新建员工档案及关联登录账号（需管理员权限） */
  create: (data) => http.post('/employees', data),
  /** PUT /employees/:id - 更新员工基本信息（需管理员权限） */
  update: (id, data) => http.put(`/employees/${id}`, data),
  /** POST /employees/:id/transfer - 员工调岗/调级（需管理员权限） */
  transfer: (id, data) => http.post(`/employees/${id}/transfer`, data),
  /** POST /employees/:id/resign - 员工离职（需管理员权限） */
  resign: (id, data) => http.post(`/employees/${id}/resign`, data),
  /** GET /employees/:id/history - 获取指定员工变动历史 */
  history: (id) => http.get(`/employees/${id}/history`),
  /** GET /employees/all-history - 获取所有员工变动历史（需管理员权限） */
  allHistory: (params) => http.get('/employees/all-history', { params }),
  /** POST /employees/test-data/seed - 批量写入测试员工数据（仅开发/演示用） */
  seedTestData: (data) => http.post('/employees/test-data/seed', data),
}

/** 考勤接口 */
export const attendanceApi = {
  /** POST /attendance/check-in - 员工签到（自动计算是否迟到） */
  checkIn: (data) => http.post('/attendance/check-in', data),
  /** POST /attendance/check-out - 员工签离 */
  checkOut: (data) => http.post('/attendance/check-out', data),
  /** POST /attendance/:id/confirm - 管理员确认/修改考勤状态并重算罚款 */
  confirm: (id, data) => http.post(`/attendance/${id}/confirm`, data),
  /** GET /attendance - 查询考勤记录列表（员工只能查自己的） */
  list: (params) => http.get('/attendance', { params }),
}

/** 薪资接口 */
export const salaryApi = {
  /** POST /salary/generate/:yearMonth - 批量生成指定月份工资单（需管理员权限） */
  generate: (yearMonth) => http.post(`/salary/generate/${yearMonth}`),
  /** POST /salary/bonus - 为指定员工设置当月奖金（需管理员权限） */
  setBonus: (data) => http.post('/salary/bonus', data),
  /** GET /salary - 查询薪资列表（员工只能查自己的，管理员可按月份/员工筛选） */
  list: (params) => http.get('/salary', { params }),
  /** GET /salary/my - 获取当前登录员工自己的全部工资记录 */
  my: () => http.get('/salary/my'),
}

/** 统计报表接口（需管理员权限） */
export const statsApi = {
  /** GET /statistics/dept-headcount - 各部门在职员工人数统计 */
  deptHeadcount: () => http.get('/statistics/dept-headcount'),
  /** GET /statistics/dept-salary - 指定月份各部门工资总额统计 */
  deptSalary: (yearMonth) => http.get('/statistics/dept-salary', { params: { year_month: yearMonth } }),
  /** GET /statistics/monthly-attendance - 指定月份全员考勤汇总统计 */
  monthlyAttend: (yearMonth) => http.get('/statistics/monthly-attendance', { params: { year_month: yearMonth } }),
}

/** 用户账号接口（需 admin 权限） */
export const userApi = {
  /** GET /users - 获取所有用户列表 */
  list: () => http.get('/users'),
  /** GET /users/me - 获取当前登录用户信息 */
  me: () => http.get('/users/me'),
  /** POST /users - 创建新用户账号 */
  create: (data) => http.post('/users', data),
  /** PUT /users/:id/toggle-active - 切换用户启用/禁用状态 */
  toggleActive: (id) => http.put(`/users/${id}/toggle-active`),
}
