"""
首次启动时写入初始数据（幂等）
"""
from decimal import Decimal
from app.database import SessionLocal
from app import models
from app.security import get_password_hash


def init_db_data():
    db = SessionLocal()
    try:
        # 级别工资
        levels = [
            ("PROBATION", "试用员工", Decimal("3000.00"), 1),
            ("REGULAR", "正式员工", Decimal("5000.00"), 2),
            ("LEADER", "组长", Decimal("7000.00"), 3),
            ("MANAGER", "部门经理", Decimal("10000.00"), 4),
            ("GM", "总经理", Decimal("20000.00"), 5),
        ]
        for code, name, salary, order in levels:
            if not db.query(models.SalaryLevel).filter(models.SalaryLevel.level_code == code).first():
                db.add(models.SalaryLevel(level_code=code, level_name=name, base_salary=salary, sort_order=order))

        # 部门
        for dept_name, desc in [("技术部", "负责系统研发"), ("人事部", "负责人员招聘"), ("财务部", "负责公司财务")]:
            if not db.query(models.Department).filter(models.Department.name == dept_name).first():
                db.add(models.Department(name=dept_name, description=desc))

        # 罚款配置
        penalties = [
            ("LATE_PENALTY", "迟到罚款（每次）", Decimal("50.00"), "迟到不超过1小时"),
            ("ABSENT_PENALTY", "缺勤罚款（每次）", Decimal("200.00"), "缺勤或迟到超过1小时"),
        ]
        for key, name, amount, desc in penalties:
            if not db.query(models.PenaltyConfig).filter(models.PenaltyConfig.config_key == key).first():
                db.add(models.PenaltyConfig(config_key=key, config_name=name, amount=amount, description=desc))

        # 管理员账号
        if not db.query(models.User).filter(models.User.username == "admin").first():
            db.add(models.User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role="admin",
            ))

        db.commit()
    finally:
        db.close()
