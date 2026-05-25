"""罚款配置路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import require_manager, get_current_user

router = APIRouter(prefix="/api/penalty-config", tags=["罚款配置"])


@router.get("", response_model=List[schemas.PenaltyConfigOut])
def list_configs(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """返回所有罚款配置项（迟到和缺勤罚款标准）。"""
    return db.query(models.PenaltyConfig).all()


@router.put("/{config_id}", response_model=schemas.PenaltyConfigOut)
def update_config(
    config_id: int,
    body: schemas.PenaltyConfigUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_manager),
):
    """更新罚款配置金额，需要管理员权限。"""
    cfg = db.query(models.PenaltyConfig).filter(models.PenaltyConfig.id == config_id).first()
    if not cfg:
        raise HTTPException(status_code=404, detail="配置不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(cfg, k, v)
    db.commit()
    db.refresh(cfg)
    return cfg
