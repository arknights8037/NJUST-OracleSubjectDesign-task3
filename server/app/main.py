"""
FastAPI 应用入口
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app import models  # noqa: F401  确保所有模型被注册
from app.routers import auth, departments, salary_levels, penalty_config, employees, attendance, salary, statistics, users
from app.init_data import init_db_data
from app.schema_validation import validate_oracle_schema

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("正在初始化数据库...")
    validate_oracle_schema(engine)
    init_db_data()
    logger.info("数据库初始化完成")
    yield


app = FastAPI(
    title=settings.app.title,
    version=settings.app.version,
    debug=settings.app.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(departments.router)
app.include_router(salary_levels.router)
app.include_router(penalty_config.router)
app.include_router(employees.router)
app.include_router(attendance.router)
app.include_router(salary.router)
app.include_router(statistics.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"message": f"{settings.app.title} API is running"}
