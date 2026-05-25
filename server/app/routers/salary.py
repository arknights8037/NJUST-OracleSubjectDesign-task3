"""工资管理路由"""
from calendar import monthrange
from decimal import Decimal
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user, require_manager

router = APIRouter(prefix="/api/salary", tags=["工资管理"])


def _build_salary_out(rec: models.SalaryRecord, db: Session) -> schemas.SalaryRecordOut:
    emp = db.query(models.Employee).filter(models.Employee.id == rec.employee_id).first()
    return schemas.SalaryRecordOut(
        id=rec.id,
        employee_id=rec.employee_id,
        employee_name=emp.name if emp else None,
        department_name=emp.department.name if emp and emp.department else None,
        level_name=emp.level.level_name if emp and emp.level else None,
        year_month=rec.year_month,
        base_salary=rec.base_salary,
        bonus=rec.bonus,
        penalty=rec.penalty,
        total_salary=rec.total_salary,
        is_confirmed=rec.is_confirmed,
        bonus_remark=rec.bonus_remark,
    )


@router.post("/generate/{year_month}")
def generate_monthly_salary(
    year_month: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_manager),
):
    """批量生成指定月份工资单（只生成还不存在的记录）。
    - 遍历所有在职员工，汇总当月考勤罚款后写入工资记录。
    - 已存在的记录跳过，保证幂等性。
    """
    employees = db.query(models.Employee).filter(models.Employee.status == "active").all()
    created = 0
    for emp in employees:
        existing = db.query(models.SalaryRecord).filter(
            models.SalaryRecord.employee_id == emp.id,
            models.SalaryRecord.year_month == year_month,
        ).first()
        if existing:
            continue
        # 计算该月自然月的起止日期，用于查询考勤罚款
        parts = year_month.split("-")
        y, m = int(parts[0]), int(parts[1])
        first_day = date(y, m, 1)
        last_day = date(y, m, monthrange(y, m)[1])
        total_penalty = db.query(models.Attendance).filter(
            models.Attendance.employee_id == emp.id,
            models.Attendance.attend_date >= first_day,
            models.Attendance.attend_date <= last_day,
        ).all()
        penalty_sum = sum(float(a.penalty_amount or 0) for a in total_penalty)

        base = float(emp.level.base_salary) if emp.level else 0
        rec = models.SalaryRecord(
            employee_id=emp.id,
            year_month=year_month,
            base_salary=Decimal(str(base)),
            bonus=Decimal("0"),
            penalty=Decimal(str(penalty_sum)),
            total_salary=Decimal(str(base - penalty_sum)),
        )
        db.add(rec)
        created += 1
    db.commit()
    return {"message": f"已生成 {created} 条工资记录"}


@router.post("/bonus", response_model=schemas.SalaryRecordOut)
def set_bonus(
    body: schemas.SalaryBonusSet,
    db: Session = Depends(get_db),
    current_user=Depends(require_manager),
):
    """为指定员工的月度工资单设置奖金，同步更新实发工资合计。"""
    rec = db.query(models.SalaryRecord).filter(
        models.SalaryRecord.employee_id == body.employee_id,
        models.SalaryRecord.year_month == body.year_month,
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="工资记录不存在，请先生成月度工资单")
    rec.bonus = body.bonus
    rec.total_salary = rec.base_salary + body.bonus - rec.penalty
    rec.bonus_set_by = current_user.id
    rec.bonus_remark = body.bonus_remark
    db.commit()
    db.refresh(rec)
    return _build_salary_out(rec, db)


@router.get("", response_model=List[schemas.SalaryRecordOut])
def list_salary(
    year_month: Optional[str] = Query(None, description="筛选月份，格式 YYYY-MM"),
    employee_id: Optional[int] = Query(None, description="按员工 ID 筛选（仅管理员有效）"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """查询工资列表。员工只能看到自己的记录；管理员可按员工 ID / 月份筛选。"""
    q = db.query(models.SalaryRecord)
    if current_user.role == "employee":
        emp = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
        if not emp:
            return []
        q = q.filter(models.SalaryRecord.employee_id == emp.id)
    elif employee_id:
        q = q.filter(models.SalaryRecord.employee_id == employee_id)

    if year_month:
        q = q.filter(models.SalaryRecord.year_month == year_month)

    return [_build_salary_out(r, db) for r in q.order_by(models.SalaryRecord.year_month.desc()).all()]


@router.get("/my", response_model=List[schemas.SalaryRecordOut])
def my_salary(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """返回当前登录员工自己的全部工资记录，按月份降序排列。"""
    emp = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
    if not emp:
        return []
    records = db.query(models.SalaryRecord).filter(
        models.SalaryRecord.employee_id == emp.id
    ).order_by(models.SalaryRecord.year_month.desc()).all()
    return [_build_salary_out(r, db) for r in records]
