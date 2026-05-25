"""
数据库连接与 Session 管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

engine = create_engine(
    settings.db.url,
    echo=settings.db.echo,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI 依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
