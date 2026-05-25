"""
配置加载模块 - 从 config.toml 读取配置
"""
import pathlib
import tomli

_CONFIG_PATH = pathlib.Path(__file__).parent.parent / "config.toml"

with open(_CONFIG_PATH, "rb") as f:
    _cfg = tomli.load(f)


class _AppConfig:
    title: str = _cfg["app"]["title"]
    version: str = _cfg["app"]["version"]
    debug: bool = _cfg["app"].get("debug", False)


class _ServerConfig:
    host: str = _cfg["server"]["host"]
    port: int = _cfg["server"]["port"]


class _DatabaseConfig:
    url: str = _cfg["database"]["url"]
    echo: bool = _cfg["database"].get("echo", False)


class _JWTConfig:
    secret_key: str = _cfg["jwt"]["secret_key"]
    algorithm: str = _cfg["jwt"]["algorithm"]
    expire_minutes: int = _cfg["jwt"]["access_token_expire_minutes"]


class _CORSConfig:
    origins: list = _cfg["cors"]["origins"]


class _AttendanceConfig:
    work_start_hour: int = _cfg["attendance"]["work_start_hour"]
    work_start_minute: int = _cfg["attendance"]["work_start_minute"]
    late_threshold_minutes: int = _cfg["attendance"]["late_threshold_minutes"]


class Settings:
    app = _AppConfig()
    server = _ServerConfig()
    db = _DatabaseConfig()
    jwt = _JWTConfig()
    cors = _CORSConfig()
    attendance = _AttendanceConfig()


settings = Settings()
