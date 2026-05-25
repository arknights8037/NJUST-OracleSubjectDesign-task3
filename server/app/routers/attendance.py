"""考勤管理路由"""
from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user, require_manager
from app.config import settings

router = APIRouter(prefix="/api/attendance", tags=["考勤管理"])


def _calc_penalty(status: str, late_minutes: int, db: Session) -> float:
    late_cfg = db.query(models.PenaltyConfig).filter(
        models.PenaltyConfig.config_key == "LATE_PENALTY"
    ).first()
    absent_cfg = db.query(models.PenaltyConfig).filter(
        models.PenaltyConfig.config_key == "ABSENT_PENALTY"
    ).first()
    late_amount = float(late_cfg.amount) if late_cfg else 50
    absent_amount = float(absent_cfg.amount) if absent_cfg else 200

    if status == "absent":
        return absent_amount
    if status == "late":
        return late_amount
    return 0.0


@router.post("/check-in", response_model=schemas.AttendanceOut)
def check_in(
    body: schemas.AttendanceCheckIn,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """员工签到接口。
    - 自动计算迟到分钟并判断考勤状态（正常/迟到/缺勤）。
    - 同一天重复签到则返回 400 错误。
    """
    emp = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
    if not emp:
        raise HTTPException(status_code=400, detail="当前用户没有关联员工档案")

    today = date.today()
    existing = db.query(models.Attendance).filter(
        models.Attendance.employee_id == emp.id,
        models.Attendance.attend_date == today,
    ).first()
    if existing and existing.check_in:
        raise HTTPException(status_code=400, detail="今日已签到")

    now = datetime.now()
    work_start = now.replace(
        hour=settings.attendance.work_start_hour,
        minute=settings.attendance.work_start_minute,
        second=0,
        microsecond=0,
    )
    late_minutes = max(0, int((now - work_start).total_seconds() / 60))
    status = "normal"
    if late_minutes > 0:
        if late_minutes >= settings.attendance.late_threshold_minutes:
            status = "absent"
        else:
            status = "late"

    penalty = _calc_penalty(status, late_minutes, db)

    if existing:
        existing.check_in = now
        existing.status = status
        existing.late_minutes = late_minutes
        existing.penalty_amount = penalty
        existing.remark = body.remark
        db.commit()
        db.refresh(existing)
        rec = existing
    else:
        rec = models.Attendance(
            employee_id=emp.id,
            attend_date=today,
            check_in=now,
            status=status,
            late_minutes=late_minutes,
            penalty_amount=penalty,
            remark=body.remark,
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)

    return schemas.AttendanceOut(
        id=rec.id, employee_id=rec.employee_id, employee_name=emp.name,
        attend_date=rec.attend_date, check_in=rec.check_in, check_out=rec.check_out,
        status=rec.status, late_minutes=rec.late_minutes,
        penalty_amount=rec.penalty_amount, remark=rec.remark, confirmed_by=rec.confirmed_by,
    )


@router.post("/check-out", response_model=schemas.AttendanceOut)
def check_out(
    body: schemas.AttendanceCheckOut,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """员工签离接口，须已完成签到才可操作，同一天重复签离返回 400 错误。"""
    emp = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
    if not emp:
        raise HTTPException(status_code=400, detail="当前用户没有关联员工档案")

    today = date.today()
    rec = db.query(models.Attendance).filter(
        models.Attendance.employee_id == emp.id,
        models.Attendance.attend_date == today,
    ).first()
    if not rec or not rec.check_in:
        raise HTTPException(status_code=400, detail="今日尚未签到")
    if rec.check_out:
        raise HTTPException(status_code=400, detail="今日已签离")

    rec.check_out = datetime.now()
    if body.remark:
        rec.remark = body.remark
    db.commit()
    db.refresh(rec)
    return schemas.AttendanceOut(
        id=rec.id, employee_id=rec.employee_id, employee_name=emp.name,
        attend_date=rec.attend_date, check_in=rec.check_in, check_out=rec.check_out,
        status=rec.status, late_minutes=rec.late_minutes,
        penalty_amount=rec.penalty_amount, remark=rec.remark, confirmed_by=rec.confirmed_by,
    )


@router.post("/{att_id}/confirm", response_model=schemas.AttendanceOut)
def confirm_attendance(
    att_id: int,
    body: schemas.AttendanceConfirm,
    db: Session = Depends(get_db),
    current_user=Depends(require_manager),
):
    """管理员确认/修改考勤状态，并重新计算对应罚款金额。"""
    rec = db.query(models.Attendance).filter(models.Attendance.id == att_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="考勤记录不存在")
    rec.status = body.status
    rec.confirmed_by = current_user.id
    if body.remark:
        rec.remark = body.remark
    # 重新计算罚款
    rec.penalty_amount = _calc_penalty(body.status, rec.late_minutes, db)
    db.commit()
    db.refresh(rec)
    emp = db.query(models.Employee).filter(models.Employee.id == rec.employee_id).first()
    return schemas.AttendanceOut(
        id=rec.id, employee_id=rec.employee_id,
        employee_name=emp.name if emp else None,
        attend_date=rec.attend_date, check_in=rec.check_in, check_out=rec.check_out,
        status=rec.status, late_minutes=rec.late_minutes,
        penalty_amount=rec.penalty_amount, remark=rec.remark, confirmed_by=rec.confirmed_by,
    )


@router.get("", response_model=List[schemas.AttendanceOut])
def list_attendance(
    employee_id: Optional[int] = Query(None, description="按员工 ID 筛选（仅管理员有效）"),
    start_date: Optional[date] = Query(None, description="查询起始日期"),
    end_date: Optional[date] = Query(None, description="查询截止日期"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """查询考勤记录列表。员工只能查自己的；管理员可按员工 ID 和日期范围筛选。"""
    q = db.query(models.Attendance)

    if current_user.role == "employee":
        emp = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
        if not emp:
            return []
        q = q.filter(models.Attendance.employee_id == emp.id)
    elif employee_id:
        q = q.filter(models.Attendance.employee_id == employee_id)

    if start_date:
        q = q.filter(models.Attendance.attend_date >= start_date)
    if end_date:
        q = q.filter(models.Attendance.attend_date <= end_date)

    records = q.order_by(models.Attendance.attend_date.desc()).all()
    result = []
    for rec in records:
        emp = db.query(models.Employee).filter(models.Employee.id == rec.employee_id).first()
        result.append(schemas.AttendanceOut(
            id=rec.id, employee_id=rec.employee_id,
            employee_name=emp.name if emp else None,
            attend_date=rec.attend_date, check_in=rec.check_in, check_out=rec.check_out,
            status=rec.status, late_minutes=rec.late_minutes,
            penalty_amount=rec.penalty_amount, remark=rec.remark, confirmed_by=rec.confirmed_by,
        ))
    return result
