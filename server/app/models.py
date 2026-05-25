"""ORM 模型定义（Oracle）"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Numeric, Date, DateTime, Identity,
    ForeignKey, UniqueConstraint, Boolean, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, Identity(), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    employees = relationship("Employee", back_populates="department")


class SalaryLevel(Base):
    __tablename__ = "salary_levels"

    id = Column(Integer, Identity(), primary_key=True)
    level_code = Column(String(50), nullable=False, unique=True)
    level_name = Column(String(100), nullable=False)
    base_salary = Column(Numeric(12, 2), nullable=False)
    description = Column(String(500))
    sort_order = Column(Integer, default=0)

    employees = relationship("Employee", back_populates="level")


class PenaltyConfig(Base):
    __tablename__ = "penalty_config"

    id = Column(Integer, Identity(), primary_key=True)
    config_key = Column(String(100), nullable=False, unique=True)
    config_name = Column(String(200), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(500))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Identity(), primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(256), nullable=False)
    role = Column("account_type", String(50), nullable=False, default="employee")  # employee / manager / admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="user", uselist=False)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, Identity(), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100), nullable=False)
    gender = Column(String(10))
    id_card = Column(String(18), unique=True, nullable=False)
    phone = Column(String(20))
    email = Column(String(200))
    department_id = Column(Integer, ForeignKey("departments.id"))
    level_id = Column(Integer, ForeignKey("salary_levels.id"))
    hire_date = Column(Date, nullable=False)
    status = Column(String(20), default="active")  # active / transferred / resigned
    resign_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="employee")
    department = relationship("Department", back_populates="employees")
    level = relationship("SalaryLevel", back_populates="employees")
    history = relationship("EmployeeHistory", back_populates="employee", foreign_keys="EmployeeHistory.employee_id")
    attendances = relationship("Attendance", back_populates="employee")
    salary_records = relationship("SalaryRecord", back_populates="employee")


class EmployeeHistory(Base):
    __tablename__ = "employee_history"

    id = Column(Integer, Identity(), primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    change_type = Column(String(50), nullable=False)  # hire/transfer/resign/level_change/salary_change
    old_department_id = Column(Integer, ForeignKey("departments.id"))
    new_department_id = Column(Integer, ForeignKey("departments.id"))
    old_level_id = Column(Integer, ForeignKey("salary_levels.id"))
    new_level_id = Column(Integer, ForeignKey("salary_levels.id"))
    old_base_salary = Column(Numeric(12, 2))
    new_base_salary = Column(Numeric(12, 2))
    remark = Column(Text)
    operated_by = Column(Integer, ForeignKey("users.id"))
    operated_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="history", foreign_keys=[employee_id])
    old_department = relationship("Department", foreign_keys=[old_department_id])
    new_department = relationship("Department", foreign_keys=[new_department_id])
    old_level = relationship("SalaryLevel", foreign_keys=[old_level_id])
    new_level = relationship("SalaryLevel", foreign_keys=[new_level_id])
    operator = relationship("User", foreign_keys=[operated_by])


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("employee_id", "attend_date"),)

    id = Column(Integer, Identity(), primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    attend_date = Column(Date, nullable=False)
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    status = Column(String(30), default="normal")  # normal/late/absent/business_trip/outside
    confirmed_by = Column(Integer, ForeignKey("users.id"))
    late_minutes = Column(Integer, default=0)
    penalty_amount = Column(Numeric(10, 2), default=0)
    remark = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="attendances")
    confirmer = relationship("User", foreign_keys=[confirmed_by])


class SalaryRecord(Base):
    __tablename__ = "salary_records"
    __table_args__ = (UniqueConstraint("employee_id", "year_month"),)

    id = Column(Integer, Identity(), primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    year_month = Column(String(7), nullable=False)   # YYYY-MM
    base_salary = Column(Numeric(12, 2), nullable=False)
    bonus = Column(Numeric(12, 2), default=0)
    penalty = Column(Numeric(12, 2), default=0)
    total_salary = Column(Numeric(12, 2), nullable=False)
    bonus_set_by = Column(Integer, ForeignKey("users.id"))
    bonus_remark = Column(String(500))
    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = relationship("Employee", back_populates="salary_records")
    bonus_setter = relationship("User", foreign_keys=[bonus_set_by])
