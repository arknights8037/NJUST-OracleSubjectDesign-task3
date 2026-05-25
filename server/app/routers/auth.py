"""认证路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=schemas.Token)
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    """用户登录接口。验证用户名和密码，校验通过后返回 JWT 令牌及角色、关联员工信息。"""
    user = db.query(models.User).filter(models.User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已禁用")

    token = create_access_token({"sub": str(user.id), "role": user.role})

    employee = db.query(models.Employee).filter(models.Employee.user_id == user.id).first()
    return schemas.Token(
        access_token=token,
        role=user.role,
        user_id=user.id,
        employee_id=employee.id if employee else None,
        name=employee.name if employee else user.username,
    )
