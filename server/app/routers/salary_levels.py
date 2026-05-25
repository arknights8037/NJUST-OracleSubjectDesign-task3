"""员工级别管理路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import require_manager, get_current_user

router = APIRouter(prefix="/api/salary-levels", tags=["级别工资配置"])


@router.get("", response_model=List[schemas.SalaryLevelOut])
def list_levels(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """返回所有薄酒等级，按显示顺序排列。"""
    return db.query(models.SalaryLevel).order_by(models.SalaryLevel.sort_order).all()


@router.post("", response_model=schemas.SalaryLevelOut)
def create_level(body: schemas.SalaryLevelCreate, db: Session = Depends(get_db), _=Depends(require_manager)):
    """新建工资等级，需要管理员权限。"""
    level = models.SalaryLevel(**body.model_dump())
    db.add(level)
    db.commit()
    db.refresh(level)
    return level


@router.put("/{level_id}", response_model=schemas.SalaryLevelOut)
def update_level(
    level_id: int,
    body: schemas.SalaryLevelUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_manager),
):
    """更新工资等级信息，支持部分字段更新，需要管理员权限。"""
    level = db.query(models.SalaryLevel).filter(models.SalaryLevel.id == level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="级别不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(level, k, v)
    db.commit()
    db.refresh(level)
    return level


@router.delete("/{level_id}")
def delete_level(level_id: int, db: Session = Depends(get_db), _=Depends(require_manager)):
    """强删除工资等级，需确保无员工关联。需要管理员权限。"""
    level = db.query(models.SalaryLevel).filter(models.SalaryLevel.id == level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="级别不存在")
    db.delete(level)
    db.commit()
    return {"message": "已删除"}
