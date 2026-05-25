"""
Pydantic 模式定义
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator


# ─── Auth ───────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    employee_id: Optional[int] = None
    name: Optional[str] = None


# ─── Department ─────────────────────────────────────────────

class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}


# ─── SalaryLevel ────────────────────────────────────────────

class SalaryLevelCreate(BaseModel):
    level_code: str
    level_name: str
    base_salary: Decimal
    description: Optional[str] = None
    sort_order: int = 0


class SalaryLevelUpdate(BaseModel):
    level_name: Optional[str] = None
    base_salary: Optional[Decimal] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class SalaryLevelOut(BaseModel):
    id: int
    level_code: str
    level_name: str
    base_salary: Decimal
    description: Optional[str]
    sort_order: int

    model_config = {"from_attributes": True}


# ─── PenaltyConfig ──────────────────────────────────────────

class PenaltyConfigUpdate(BaseModel):
    amount: Decimal
    description: Optional[str] = None


class PenaltyConfigOut(BaseModel):
    id: int
    config_key: str
    config_name: str
    amount: Decimal
    description: Optional[str]

    model_config = {"from_attributes": True}


# ─── User ───────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "employee"


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


# ─── Employee ───────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    name: str
    gender: Optional[str] = None
    id_card: str
    phone: Optional[str] = None
    email: Optional[str] = None
    department_id: int
    level_id: int
    hire_date: date
    username: str          # 自动创建登录账号
    password: str
    role: str = "employee"


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    level_id: Optional[int] = None
    hire_date: Optional[date] = None


class TestDataSeedRequest(BaseModel):
    employee_count: int = 12
    year_month: Optional[str] = None
    include_attendance: bool = True
    generate_salary: bool = True

    @field_validator("employee_count")
    @classmethod
    def validate_employee_count(cls, value: int):
        if value < 1 or value > 100:
            raise ValueError("员工数量必须在 1 到 100 之间")
        return value

    @field_validator("year_month")
    @classmethod
    def validate_year_month(cls, value: Optional[str]):
        if value is None or value == "":
            return None
        try:
            year, month = value.split("-")
            if len(year) != 4 or len(month) != 2:
                raise ValueError
            month_int = int(month)
            if month_int < 1 or month_int > 12:
                raise ValueError
        except ValueError as exc:
            raise ValueError("年月格式必须为 YYYY-MM") from exc
        return value


class TestDataSeedOut(BaseModel):
    employee_count: int
    attendance_count: int
    salary_count: int
    year_month: str
    initial_password: str
    usernames: List[str]


class EmployeeTransfer(BaseModel):
    new_department_id: Optional[int] = None
    new_level_id: Optional[int] = None
    remark: Optional[str] = None


class EmployeeResign(BaseModel):
    resign_date: date
    remark: Optional[str] = None


class EmployeeOut(BaseModel):
    id: int
    name: str
    gender: Optional[str]
    id_card: str
    phone: Optional[str]
    email: Optional[str]
    department_id: Optional[int]
    department_name: Optional[str] = None
    level_id: Optional[int]
    level_name: Optional[str] = None
    base_salary: Optional[Decimal] = None
    hire_date: date
    status: str
    resign_date: Optional[date]
    user_id: Optional[int]
    username: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── EmployeeHistory ────────────────────────────────────────

class EmployeeHistoryOut(BaseModel):
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    change_type: str
    old_department_id: Optional[int]
    old_department_name: Optional[str] = None
    new_department_id: Optional[int]
    new_department_name: Optional[str] = None
    old_level_id: Optional[int]
    old_level_name: Optional[str] = None
    new_level_id: Optional[int]
    new_level_name: Optional[str] = None
    old_base_salary: Optional[Decimal]
    new_base_salary: Optional[Decimal]
    remark: Optional[str]
    operated_by: Optional[int]
    operator_name: Optional[str] = None
    operated_at: datetime

    model_config = {"from_attributes": True}


# ─── Attendance ─────────────────────────────────────────────

class AttendanceCheckIn(BaseModel):
    remark: Optional[str] = None


class AttendanceCheckOut(BaseModel):
    remark: Optional[str] = None


class AttendanceConfirm(BaseModel):
    status: str  # normal / business_trip / outside
    remark: Optional[str] = None


class AttendanceOut(BaseModel):
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    attend_date: date
    check_in: Optional[datetime]
    check_out: Optional[datetime]
    status: str
    late_minutes: int
    penalty_amount: Decimal
    remark: Optional[str]
    confirmed_by: Optional[int]

    model_config = {"from_attributes": True}


# ─── SalaryRecord ───────────────────────────────────────────

class SalaryBonusSet(BaseModel):
    employee_id: int
    year_month: str
    bonus: Decimal
    bonus_remark: Optional[str] = None


class SalaryRecordOut(BaseModel):
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    department_name: Optional[str] = None
    level_name: Optional[str] = None
    year_month: str
    base_salary: Decimal
    bonus: Decimal
    penalty: Decimal
    total_salary: Decimal
    is_confirmed: bool
    bonus_remark: Optional[str]

    model_config = {"from_attributes": True}


# ─── Statistics ─────────────────────────────────────────────

class DeptStatOut(BaseModel):
    department_name: str
    employee_count: int
    total_salary: Decimal


class MonthAttendStatOut(BaseModel):
    employee_id: int
    employee_name: str
    total_days: int
    normal_days: int
    late_days: int
    absent_days: int
    trip_days: int
    outside_days: int
    total_penalty: Decimal
