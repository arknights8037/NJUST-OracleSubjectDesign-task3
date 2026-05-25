"""部门管理路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import require_manager, get_current_user

router = APIRouter(prefix="/api/departments", tags=["部门管理"])


@router.get("", response_model=List[schemas.DepartmentOut])
def list_departments(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """返回所有部门列表（包含已停用部门），所有登录用户均可访问。"""
    return db.query(models.Department).all()


@router.post("", response_model=schemas.DepartmentOut)
def create_department(
    body: schemas.DepartmentCreate,
    db: Session = Depends(get_db),
    _=Depends(require_manager),
):
    """新建部门，需要管理员权限。"""
    dept = models.Department(**body.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.put("/{dept_id}", response_model=schemas.DepartmentOut)
def update_department(
    dept_id: int,
    body: schemas.DepartmentUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_manager),
):
    """更新部门信息，支持部分字段更新（PATCH 语义），需要管理员权限。"""
    dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(dept, k, v)
    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/{dept_id}")
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_manager),
):
    """停用指定部门（软删除，将 is_active 置为 False），需要管理员权限。"""
    dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    dept.is_active = False
    db.commit()
    return {"message": "已停用"}
