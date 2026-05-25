-- ============================================================
-- 员工人事工资考勤管理系统 - Oracle DDL 初始化脚本
-- 用户: zwb / 123456  服务名: XEPDB1
-- ============================================================

-- 部门表
CREATE TABLE departments (
    id          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR2(100)  NOT NULL UNIQUE,
    description VARCHAR2(500),
    created_at  TIMESTAMP DEFAULT SYSTIMESTAMP,
    is_active   NUMBER(1) DEFAULT 1
);

-- 员工级别与基本工资配置表
CREATE TABLE salary_levels (
    id            NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    level_code    VARCHAR2(50)   NOT NULL UNIQUE,  -- 如 PROBATION, REGULAR, LEADER, MANAGER, GM
    level_name    VARCHAR2(100)  NOT NULL,
    base_salary   NUMBER(12, 2)  NOT NULL,
    description   VARCHAR2(500),
    sort_order    NUMBER DEFAULT 0
);

-- 罚款配置表
CREATE TABLE penalty_config (
    id          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    config_key  VARCHAR2(100) NOT NULL UNIQUE,
    config_name VARCHAR2(200) NOT NULL,
    amount      NUMBER(10, 2) NOT NULL,
    description VARCHAR2(500),
    updated_at  TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- 用户表（用于登录认证）
CREATE TABLE users (
    id            NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username      VARCHAR2(100) NOT NULL UNIQUE,
    hashed_password VARCHAR2(256) NOT NULL,
    account_type  VARCHAR2(50)  DEFAULT 'employee' NOT NULL,  -- employee, manager, admin
    is_active     NUMBER(1) DEFAULT 1,
    created_at    TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- 员工档案表
CREATE TABLE employees (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id         NUMBER REFERENCES users(id),
    name            VARCHAR2(100) NOT NULL,
    gender          VARCHAR2(10),   -- 男/女
    id_card         VARCHAR2(18) UNIQUE NOT NULL,
    phone           VARCHAR2(20),
    email           VARCHAR2(200),
    department_id   NUMBER REFERENCES departments(id),
    level_id        NUMBER REFERENCES salary_levels(id),
    hire_date       DATE NOT NULL,
    status          VARCHAR2(20) DEFAULT 'active',  -- active, transferred, resigned
    resign_date     DATE,
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
    updated_at      TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- 员工变动历史表
CREATE TABLE employee_history (
    id                  NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id         NUMBER NOT NULL REFERENCES employees(id),
    change_type         VARCHAR2(50) NOT NULL,  -- hire, transfer, resign, level_change, salary_change
    old_department_id   NUMBER REFERENCES departments(id),
    new_department_id   NUMBER REFERENCES departments(id),
    old_level_id        NUMBER REFERENCES salary_levels(id),
    new_level_id        NUMBER REFERENCES salary_levels(id),
    old_base_salary     NUMBER(12, 2),
    new_base_salary     NUMBER(12, 2),
    remark              VARCHAR2(1000),
    operated_by         NUMBER REFERENCES users(id),
    operated_at         TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- 考勤记录表
CREATE TABLE attendance (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id     NUMBER NOT NULL REFERENCES employees(id),
    attend_date     DATE NOT NULL,
    check_in        TIMESTAMP,
    check_out       TIMESTAMP,
    status          VARCHAR2(30) DEFAULT 'normal',  -- normal, late, absent, business_trip, outside
    confirmed_by    NUMBER REFERENCES users(id),
    late_minutes    NUMBER DEFAULT 0,
    penalty_amount  NUMBER(10, 2) DEFAULT 0,
    remark          VARCHAR2(500),
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
    UNIQUE (employee_id, attend_date)
);

-- 工资记录表
CREATE TABLE salary_records (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id     NUMBER NOT NULL REFERENCES employees(id),
    year_month      VARCHAR2(7) NOT NULL,   -- 格式: YYYY-MM
    base_salary     NUMBER(12, 2) NOT NULL,
    bonus           NUMBER(12, 2) DEFAULT 0,
    penalty         NUMBER(12, 2) DEFAULT 0,
    total_salary    NUMBER(12, 2) NOT NULL,
    bonus_set_by    NUMBER REFERENCES users(id),
    bonus_remark    VARCHAR2(500),
    is_confirmed    NUMBER(1) DEFAULT 0,
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
    updated_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
    UNIQUE (employee_id, year_month)
);

-- ============================================================
-- 初始化基础数据
-- ============================================================

-- 员工级别与基本工资
INSERT INTO salary_levels (level_code, level_name, base_salary, sort_order) VALUES
    ('PROBATION', '试用员工', 3000.00, 1);
INSERT INTO salary_levels (level_code, level_name, base_salary, sort_order) VALUES
    ('REGULAR', '正式员工', 5000.00, 2);
INSERT INTO salary_levels (level_code, level_name, base_salary, sort_order) VALUES
    ('LEADER', '组长', 7000.00, 3);
INSERT INTO salary_levels (level_code, level_name, base_salary, sort_order) VALUES
    ('MANAGER', '部门经理', 10000.00, 4);
INSERT INTO salary_levels (level_code, level_name, base_salary, sort_order) VALUES
    ('GM', '总经理', 20000.00, 5);

-- 部门
INSERT INTO departments (name, description) VALUES ('技术部', '负责系统研发与维护');
INSERT INTO departments (name, description) VALUES ('人事部', '负责人员招聘与管理');
INSERT INTO departments (name, description) VALUES ('财务部', '负责公司财务管理');

-- 罚款配置
INSERT INTO penalty_config (config_key, config_name, amount, description) VALUES
    ('LATE_PENALTY', '迟到罚款（每次）', 50.00, '迟到但不超过1小时的罚款金额');
INSERT INTO penalty_config (config_key, config_name, amount, description) VALUES
    ('ABSENT_PENALTY', '缺勤罚款（每次）', 200.00, '缺勤或迟到超过1小时视为缺勤的罚款金额');

-- 初始管理员账号 admin / admin123 (bcrypt hash)
-- 密码: admin123
INSERT INTO users (username, hashed_password, account_type) VALUES
    ('admin', '$2b$12$VK7D7mht7DwJ3ujQGa7ZM..uNPT2XfdCXqEj3TBXHnthlPk8BWg0u', 'admin');

COMMIT;
