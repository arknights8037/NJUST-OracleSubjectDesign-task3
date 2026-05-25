"""员工档案管理路由"""
from calendar import monthrange
from datetime import date, datetime, timedelta
from decimal import Decimal
from random import Random
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import require_manager, get_current_user
from app.security import get_password_hash

router = APIRouter(prefix="/api/employees", tags=["员工档案"])


def _month_range(year_month: str) -> tuple[date, date]:
    year, month = map(int, year_month.split("-"))
    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def _month_workdays(year_month: str) -> List[date]:
    first_day, last_day = _month_range(year_month)
    workdays = []
    current = first_day
    while current <= last_day:
      if current.weekday() < 5:
          workdays.append(current)
      current += timedelta(days=1)
    return workdays


def _build_test_id_card(serial: int) -> str:
    return f"43052419900101{serial:04d}"


def _build_test_phone(serial: int) -> str:
    return f"139{serial:08d}"


def _penalty_amounts(db: Session) -> tuple[Decimal, Decimal]:
    late_cfg = db.query(models.PenaltyConfig).filter(
        models.PenaltyConfig.config_key == "LATE_PENALTY"
    ).first()
    absent_cfg = db.query(models.PenaltyConfig).filter(
        models.PenaltyConfig.config_key == "ABSENT_PENALTY"
    ).first()
    late_amount = Decimal(str(late_cfg.amount if late_cfg else 50))
    absent_amount = Decimal(str(absent_cfg.amount if absent_cfg else 200))
    return late_amount, absent_amount


def _build_out(emp: models.Employee) -> schemas.EmployeeOut:
    return schemas.EmployeeOut(
        id=emp.id,
        name=emp.name,
        gender=emp.gender,
        id_card=emp.id_card,
        phone=emp.phone,
        email=emp.email,
        department_id=emp.department_id,
        department_name=emp.department.name if emp.department else None,
        level_id=emp.level_id,
        level_name=emp.level.level_name if emp.level else None,
        base_salary=emp.level.base_salary if emp.level else None,
        hire_date=emp.hire_date,
        status=emp.status,
        resign_date=emp.resign_date,
        user_id=emp.user_id,
        username=emp.user.username if emp.user else None,
    )


@router.get("", response_model=List[schemas.EmployeeOut])
def list_employees(
    name: Optional[str] = Query(None, description="按姓名模糊搜索"),
    department_id: Optional[int] = Query(None, description="按部门 ID 筛选"),
    level_id: Optional[int] = Query(None, description="按工资等级筛选"),
    status: Optional[str] = Query(None, description="员工状态：active/transferred/resigned"),
    hire_date_from: Optional[date] = Query(None),
    hire_date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """查询员工列表，支持按姓名/部门/等级/状态/入职日期组合筛选。"""
    q = db.query(models.Employee)
    if name:
        q = q.filter(models.Employee.name.ilike(f"%{name}%"))
    if department_id:
        q = q.filter(models.Employee.department_id == department_id)
    if level_id:
        q = q.filter(models.Employee.level_id == level_id)
    if status:
        q = q.filter(models.Employee.status == status)
    if hire_date_from:
        q = q.filter(models.Employee.hire_date >= hire_date_from)
    if hire_date_to:
        q = q.filter(models.Employee.hire_date <= hire_date_to)
    return [_build_out(e) for e in q.all()]


@router.post("/test-data/seed", response_model=schemas.TestDataSeedOut)
def seed_test_data(
    body: schemas.TestDataSeedRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_manager),
):
    """批量写入测试员工数据。
    - 自动生成指定数量员工及其登录账号。
    - 可选生成对应月份的考勤记录和工资单。
    - 仅用于开发测试，初始密码均为 test123456。
    """
    year_month = body.year_month or date.today().strftime("%Y-%m")
    workdays = _month_workdays(year_month)
    departments = db.query(models.Department).order_by(models.Department.id.asc()).all()
    levels = db.query(models.SalaryLevel).order_by(models.SalaryLevel.sort_order.asc(), models.SalaryLevel.id.asc()).all()

    if not departments or not levels:
        raise HTTPException(status_code=400, detail="请先初始化部门和级别数据")

    next_serial = (db.query(func.max(models.User.id)).scalar() or 0) + 1
    hire_date = _month_range(year_month)[0]
    late_amount, absent_amount = _penalty_amounts(db)
    rng = Random(f"seed:{year_month}:{body.employee_count}:{next_serial}")
    default_password = "test123456"

    created_employees = []
    usernames = []
    attendance_count = 0
    salary_count = 0

    for offset in range(body.employee_count):
        serial = next_serial + offset
        username = f"test_emp_{serial}"
        user = models.User(
            username=username,
            hashed_password=get_password_hash(default_password),
            role="employee",
        )
        db.add(user)
        db.flush()

        department = departments[offset % len(departments)]
        level = levels[offset % len(levels)]
        employee = models.Employee(
            user_id=user.id,
            name=f"测试员工{serial}",
            gender="男" if offset % 2 == 0 else "女",
            id_card=_build_test_id_card(serial),
            phone=_build_test_phone(serial),
            email=f"test_emp_{serial}@example.com",
            department_id=department.id,
            level_id=level.id,
            hire_date=hire_date,
            status="active",
        )
        db.add(employee)
        db.flush()

        db.add(models.EmployeeHistory(
            employee_id=employee.id,
            change_type="hire",
            new_department_id=department.id,
            new_level_id=level.id,
            new_base_salary=level.base_salary,
            remark="批量写入测试数据",
            operated_by=current_user.id,
        ))

        if body.include_attendance:
            for workday in workdays:
                roll = rng.random()
                status = "normal"
                late_minutes = 0
                penalty_amount = Decimal("0")
                check_in = datetime.combine(workday, datetime.min.time()).replace(hour=8, minute=58)
                check_out = datetime.combine(workday, datetime.min.time()).replace(hour=18, minute=6)

                if roll > 0.92:
                    status = "outside"
                elif roll > 0.85:
                    status = "business_trip"
                elif roll > 0.76:
                    status = "late"
                    late_minutes = rng.randint(8, 35)
                    penalty_amount = late_amount
                    check_in = check_in + timedelta(minutes=late_minutes)
                elif roll > 0.70:
                    status = "absent"
                    penalty_amount = absent_amount
                    check_in = None
                    check_out = None

                db.add(models.Attendance(
                    employee_id=employee.id,
                    attend_date=workday,
                    check_in=check_in,
                    check_out=check_out,
                    status=status,
                    late_minutes=late_minutes,
                    penalty_amount=penalty_amount,
                    remark="批量测试数据",
                    confirmed_by=current_user.id if status in ("business_trip", "outside") else None,
                ))
                attendance_count += 1

        created_employees.append(employee)
        usernames.append(username)

    db.flush()

    if body.generate_salary:
        for employee in created_employees:
            existing = db.query(models.SalaryRecord).filter(
                models.SalaryRecord.employee_id == employee.id,
                models.SalaryRecord.year_month == year_month,
            ).first()
            if existing:
                continue

            monthly_penalty = db.query(func.coalesce(func.sum(models.Attendance.penalty_amount), 0)).filter(
                models.Attendance.employee_id == employee.id,
                models.Attendance.attend_date >= hire_date,
                models.Attendance.attend_date <= _month_range(year_month)[1],
            ).scalar()
            bonus = Decimal(str(rng.choice([0, 200, 500, 800])))
            base_salary = Decimal(str(employee.level.base_salary if employee.level else 0))
            penalty = Decimal(str(monthly_penalty or 0))

            db.add(models.SalaryRecord(
                employee_id=employee.id,
                year_month=year_month,
                base_salary=base_salary,
                bonus=bonus,
                penalty=penalty,
                total_salary=base_salary + bonus - penalty,
                bonus_set_by=current_user.id,
                bonus_remark="批量测试数据自动生成",
                is_confirmed=False,
            ))
            salary_count += 1

    db.commit()

    return schemas.TestDataSeedOut(
        employee_count=len(created_employees),
        attendance_count=attendance_count,
        salary_count=salary_count,
        year_month=year_month,
        initial_password=default_password,
        usernames=usernames,
    )


@router.get("/all-history", response_model=List[schemas.EmployeeHistoryOut])
def get_all_history(
    db: Session = Depends(get_db),
    _=Depends(require_manager),
):
    """返回全部员工变动历史（管理员权限）"""
    # 预加载所有员工，避免 N+1
    emp_dict = {e.id: e for e in db.query(models.Employee).all()}
    records = db.query(models.EmployeeHistory).order_by(
        models.EmployeeHistory.operated_at.desc()
    ).all()
    result = []
    for r in records:
        emp = emp_dict.get(r.employee_id)
        result.append(schemas.EmployeeHistoryOut(
            id=r.id,
            employee_id=r.employee_id,
            employee_name=emp.name if emp else None,
            change_type=r.change_type,
            old_department_id=r.old_department_id,
            old_department_name=r.old_department.name if r.old_department else None,
            new_department_id=r.new_department_id,
            new_department_name=r.new_department.name if r.new_department else None,
            old_level_id=r.old_level_id,
            old_level_name=r.old_level.level_name if r.old_level else None,
            new_level_id=r.new_level_id,
            new_level_name=r.new_level.level_name if r.new_level else None,
            old_base_salary=r.old_base_salary,
            new_base_salary=r.new_base_salary,
            remark=r.remark,
            operated_by=r.operated_by,
            operator_name=r.operator.username if r.operator else None,
            operated_at=r.operated_at,
        ))
    return result


@router.get("/{emp_id}", response_model=schemas.EmployeeOut)
def get_employee(emp_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    emp = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    # 普通员工只能看自己
    if current_user.role == "employee":
        my_emp = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
        if not my_emp or my_emp.id != emp_id:
            raise HTTPException(status_code=403, detail="无权查看他人信息")
    return _build_out(emp)


@router.post("", response_model=schemas.EmployeeOut)
def create_employee(
    body: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_manager),
):
    # 创建用户账号
    existing = db.query(models.User).filter(models.User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = models.User(
        username=body.username,
        hashed_password=get_password_hash(body.password),
        role=body.role,
    )
    db.add(user)
    db.flush()

    level = db.query(models.SalaryLevel).filter(models.SalaryLevel.id == body.level_id).first()
    emp = models.Employee(
        user_id=user.id,
        name=body.name,
        gender=body.gender,
        id_card=body.id_card,
        phone=body.phone,
        email=body.email,
        department_id=body.department_id,
        level_id=body.level_id,
        hire_date=body.hire_date,
    )
    db.add(emp)
    db.flush()

    # 记录入职历史
    hist = models.EmployeeHistory(
        employee_id=emp.id,
        change_type="hire",
        new_department_id=body.department_id,
        new_level_id=body.level_id,
        new_base_salary=level.base_salary if level else None,
        remark="入职",
        operated_by=current_user.id,
    )
    db.add(hist)
    db.commit()
    db.refresh(emp)
    return _build_out(emp)


@router.put("/{emp_id}", response_model=schemas.EmployeeOut)
def update_employee(
    emp_id: int,
    body: schemas.EmployeeUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_manager),
):
    emp = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(emp, k, v)
    db.commit()
    db.refresh(emp)
    return _build_out(emp)


@router.post("/{emp_id}/transfer", response_model=schemas.EmployeeOut)
def transfer_employee(
    emp_id: int,
    body: schemas.EmployeeTransfer,
    db: Session = Depends(get_db),
    current_user=Depends(require_manager),
):
    emp = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")

    old_dept = emp.department_id
    old_level = emp.level_id
    old_salary = emp.level.base_salary if emp.level else None

    if body.new_department_id:
        emp.department_id = body.new_department_id
    if body.new_level_id:
        emp.level_id = body.new_level_id

    new_level = db.query(models.SalaryLevel).filter(models.SalaryLevel.id == emp.level_id).first()
    hist = models.EmployeeHistory(
        employee_id=emp.id,
        change_type="transfer",
        old_department_id=old_dept,
        new_department_id=emp.department_id,
        old_level_id=old_level,
        new_level_id=emp.level_id,
        old_base_salary=old_salary,
        new_base_salary=new_level.base_salary if new_level else old_salary,
        remark=body.remark,
        operated_by=current_user.id,
    )
    db.add(hist)
    db.commit()
    db.refresh(emp)
    return _build_out(emp)


@router.post("/{emp_id}/resign", response_model=schemas.EmployeeOut)
def resign_employee(
    emp_id: int,
    body: schemas.EmployeeResign,
    db: Session = Depends(get_db),
    current_user=Depends(require_manager),
):
    emp = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")

    emp.status = "resigned"
    emp.resign_date = body.resign_date

    hist = models.EmployeeHistory(
        employee_id=emp.id,
        change_type="resign",
        old_department_id=emp.department_id,
        old_level_id=emp.level_id,
        old_base_salary=emp.level.base_salary if emp.level else None,
        remark=body.remark,
        operated_by=current_user.id,
    )
    db.add(hist)
    db.commit()
    db.refresh(emp)
    return _build_out(emp)


@router.get("/{emp_id}/history", response_model=List[schemas.EmployeeHistoryOut])
def get_history(
    emp_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    emp = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    if current_user.role == "employee":
        my_emp = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
        if not my_emp or my_emp.id != emp_id:
            raise HTTPException(status_code=403, detail="无权查看")
    records = db.query(models.EmployeeHistory).filter(
        models.EmployeeHistory.employee_id == emp_id
    ).order_by(models.EmployeeHistory.operated_at.desc()).all()

    result = []
    for r in records:
        result.append(schemas.EmployeeHistoryOut(
            id=r.id,
            employee_id=r.employee_id,
            employee_name=emp.name,
            change_type=r.change_type,
            old_department_id=r.old_department_id,
            old_department_name=r.old_department.name if r.old_department else None,
            new_department_id=r.new_department_id,
            new_department_name=r.new_department.name if r.new_department else None,
            old_level_id=r.old_level_id,
            old_level_name=r.old_level.level_name if r.old_level else None,
            new_level_id=r.new_level_id,
            new_level_name=r.new_level.level_name if r.new_level else None,
            old_base_salary=r.old_base_salary,
            new_base_salary=r.new_base_salary,
            remark=r.remark,
            operated_by=r.operated_by,
            operator_name=r.operator.username if r.operator else None,
            operated_at=r.operated_at,
        ))
    return result
