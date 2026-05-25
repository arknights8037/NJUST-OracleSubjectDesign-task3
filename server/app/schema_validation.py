"""Oracle schema validation utilities."""
from sqlalchemy import text


REQUIRED_TABLES = {
    "departments",
    "salary_levels",
    "penalty_config",
    "users",
    "employees",
    "employee_history",
    "attendance",
    "salary_records",
}

REQUIRED_IDENTITY_COLUMNS = {
    ("departments", "id"),
    ("salary_levels", "id"),
    ("penalty_config", "id"),
    ("users", "id"),
    ("employees", "id"),
    ("employee_history", "id"),
    ("attendance", "id"),
    ("salary_records", "id"),
}


def validate_oracle_schema(engine) -> None:
    if engine.dialect.name != "oracle":
        raise RuntimeError("当前系统仅支持 Oracle 数据库。")

    with engine.connect() as conn:
        tables = {
            row[0].lower()
            for row in conn.execute(text("SELECT table_name FROM user_tables"))
        }
        missing_tables = sorted(REQUIRED_TABLES - tables)
        if missing_tables:
            raise RuntimeError(
                "Oracle 表结构未初始化，请先执行 database/init.sql。缺失表: "
                + ", ".join(missing_tables)
            )

        identity_columns = {
            (row[0].lower(), row[1].lower())
            for row in conn.execute(
                text("SELECT table_name, column_name FROM user_tab_identity_cols")
            )
        }
        missing_identity = sorted(
            table for table, column in REQUIRED_IDENTITY_COLUMNS
            if (table, column) not in identity_columns
        )
        if missing_identity:
            raise RuntimeError(
                "Oracle 表结构不是受支持的正式结构，请清理旧表后重新执行 database/init.sql。受影响表: "
                + ", ".join(missing_identity)
            )