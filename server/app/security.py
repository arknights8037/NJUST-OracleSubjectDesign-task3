"""
安全工具：JWT 生成/验证、密码哈希
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt.expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    payload = _decode_token(token)
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="无效的认证凭据")
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user


def require_manager(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role not in ("manager", "admin"):
        raise HTTPException(status_code=403, detail="权限不足，需要经理及以上权限")
    return current_user


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足，需要管理员权限")
    return current_user
