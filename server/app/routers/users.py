"""用户管理路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import require_admin, get_current_user, get_password_hash

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    """返回所有用户列表，仅 admin 可访问。"""
    return db.query(models.User).all()


@router.post("", response_model=schemas.UserOut)
def create_user(body: schemas.UserCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    """新建登录用户，仅 admin 可操作。密码使用 bcrypt 哈希后存储。"""
    existing = db.query(models.User).filter(models.User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = models.User(
        username=body.username,
        hashed_password=get_password_hash(body.password),
        role=body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/toggle-active")
def toggle_active(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    """切换用户启用/禁用状态，仅 admin 可操作。"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_active = not user.is_active
    db.commit()
    return {"is_active": user.is_active}


@router.get("/me", response_model=schemas.UserOut)
def me(current_user=Depends(get_current_user)):
    """返回当前登录用户的基本信息。"""
    return current_user
