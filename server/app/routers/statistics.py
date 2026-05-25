"""统计报表路由"""
from calendar import monthrange
from datetime import date
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models, schemas
from app.database import get_db
from app.security import require_manager

router = APIRouter(prefix="/api/statistics", tags=["统计报表"])


@router.get("/dept-headcount", response_model=List[schemas.DeptStatOut])
def dept_headcount(db: Session = Depends(get_db), _=Depends(require_manager)):
    """统计各部门当前在职员工数，使用 LEFT JOIN 确保无员部门也包含在内。"""
    rows = (
        db.query(
            models.Department.name,
            func.count(models.Employee.id).label("cnt"),
        )
        .outerjoin(models.Employee, (models.Employee.department_id == models.Department.id)
                   & (models.Employee.status == "active"))
        .group_by(models.Department.name)
        .all()
    )
    return [
        schemas.DeptStatOut(
            department_name=r.name,
            employee_count=r.cnt,
            total_salary=Decimal("0"),
        )
        for r in rows
    ]


@router.get("/dept-salary")
def dept_salary(year_month: str = Query(..., description="查询月份，YYYY-MM"), db: Session = Depends(get_db), _=Depends(require_manager)):
    """按部门汇总指定月份工资总额，返回各部门員工人数及工资合计。"""
    rows = (
        db.query(
            models.Department.name,
            func.count(models.SalaryRecord.id).label("cnt"),
            func.sum(models.SalaryRecord.total_salary).label("total"),
        )
        .join(models.Employee, models.Employee.id == models.SalaryRecord.employee_id)
        .join(models.Department, models.Department.id == models.Employee.department_id)
        .filter(models.SalaryRecord.year_month == year_month)
        .group_by(models.Department.name)
        .all()
    )
    return [{"department_name": r.name, "employee_count": r.cnt, "total_salary": float(r.total or 0)} for r in rows]


@router.get("/monthly-attendance")
def monthly_attendance(
    year_month: str = Query(..., description="查询月份，YYYY-MM"),
    db: Session = Depends(get_db),
    _=Depends(require_manager),
):
    """按月统计所有在职员工的考勤情况，包含正常/迟到/缺勤/出差/外勤天数和罚款合计。"""
    parts = year_month.split("-")
    y, m = int(parts[0]), int(parts[1])
    first_day = date(y, m, 1)
    last_day = date(y, m, monthrange(y, m)[1])

    employees = db.query(models.Employee).filter(models.Employee.status == "active").all()
    result = []
    for emp in employees:
        recs = db.query(models.Attendance).filter(
            models.Attendance.employee_id == emp.id,
            models.Attendance.attend_date >= first_day,
            models.Attendance.attend_date <= last_day,
        ).all()
        stat = schemas.MonthAttendStatOut(
            employee_id=emp.id,
            employee_name=emp.name,
            total_days=len(recs),
            normal_days=sum(1 for r in recs if r.status == "normal"),
            late_days=sum(1 for r in recs if r.status == "late"),
            absent_days=sum(1 for r in recs if r.status == "absent"),
            trip_days=sum(1 for r in recs if r.status == "business_trip"),
            outside_days=sum(1 for r in recs if r.status == "outside"),
            total_penalty=Decimal(str(sum(float(r.penalty_amount or 0) for r in recs))),
        )
        result.append(stat)
    return result
