# 员工人事工资考勤管理系统

基于 **Oracle + FastAPI + Vue3 + Element Plus** 的全栈人事管理系统。

---

## 项目结构

```
zwb-item3/
├── database/
│   └── init.sql          # Oracle DDL 及初始数据
├── server/               # FastAPI 后端
│   ├── config.toml       # 配置文件（TOML）
│   ├── requirements.txt
│   ├── run.py            # 启动入口
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       ├── security.py
│       ├── init_data.py
│       └── routers/
│           ├── auth.py
│           ├── departments.py
│           ├── salary_levels.py
│           ├── penalty_config.py
│           ├── employees.py
│           ├── attendance.py
│           ├── salary.py
│           ├── statistics.py
│           └── users.py
└── client/               # Vue3 前端
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── api/
        ├── stores/
        ├── router/
        └── views/
```

---

## 快速启动（Oracle）

### 1. 后端

```powershell
cd server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

后端默认运行在 `http://localhost:8000`，API 文档：`http://localhost:8000/docs`

初始账号：**admin / admin123**（角色：管理员）

启动前请先用 `zwb` 用户执行 [database/init.sql](f:\OracleStudy\zwb-item3\database\init.sql) 初始化 Oracle 表结构和基础数据。

### 2. 前端

```powershell
cd client
npm install   # 或 pnpm install
npm run dev
```

前端默认运行在 `http://localhost:5173`

---

## 功能清单

| 模块 | 功能 | 权限 |
|------|------|------|
| 登录 | JWT 认证 | 全员 |
| 仪表盘 | 统计卡片、快捷打卡 | 全员 |
| 员工档案 | CRUD、调动、离职 | 经理+ |
| 变动历史 | 查询员工所有变动记录 | 全员(仅本人)/经理+ |
| 考勤打卡 | 签到/签离，自动计算迟到 | 全员 |
| 考勤确认 | 修改状态（出差/外出等） | 经理+ |
| 我的工资 | 查看本人工资记录 | 全员 |
| 工资管理 | 批量生成、设置奖金 | 经理+ |
| 部门管理 | CRUD | 经理+ |
| 级别配置 | 级别与工资对应 | 经理+ |
| 罚款配置 | 迟到/缺勤罚款金额 | 经理+ |
| 统计报表 | 部门人员/工资/考勤统计，导出Excel | 经理+ |

---

## 生产构建前端

```powershell
cd client
npm run build
# 产物在 dist/ 目录，部署到 Nginx 或任意静态服务器
```
