import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


# 手动加载.env文件
def load_env_file():
    """手动加载.env文件"""
    env_file_path = PROJECT_ROOT / ".env"
    if env_file_path.exists():
        with open(env_file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value


# 在导入配置类之前加载环境变量
load_env_file()

# 验证环境变量是否被加载
print(
    f"环境变量加载状态: LLM_GOOGLE_API_KEY = {os.getenv('LLM_GOOGLE_API_KEY', '未设置')}"
)


class DatabaseSettings(BaseSettings):
    """数据库配置"""

    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = "password"
    database: str = "test_db"

    model_config = SettingsConfigDict(env_prefix="MYSQL_", extra="ignore")

    @property
    def config_dict(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "username": self.user,
            "password": self.password,
            "database": self.database,
        }


class RedisSettings(BaseSettings):
    """Redis配置"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0

    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="ignore")

    @property
    def config_dict(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "db": self.db,
        }


class LogSettings(BaseSettings):
    """日志配置"""

    level: str = "INFO"
    format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"

    model_config = SettingsConfigDict(env_prefix="LOG_", extra="ignore")


class LLMSettings(BaseSettings):
    """LLM配置"""

    model: str = Field(default="gemini-pro", alias="LLM_MODEL")
    api_key: str = Field(default="", alias="LLM_GOOGLE_API_KEY")
    temperature: float = Field(default=0.7, alias="LLM_TEMPERATURE")
    timeout: int = Field(default=120, alias="LLM_TIMEOUT")

    model_config = SettingsConfigDict(
        extra="ignore",
    )

    @property
    def config_dict(self) -> dict:
        return {
            "model": self.model,
            "api_key": self.api_key,
            "temperature": self.temperature,
            "timeout": self.timeout,
        }


class AppSettings(BaseSettings):
    """应用配置"""

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    model_config = SettingsConfigDict(env_prefix="APP_", extra="ignore")

    @property
    def config_dict(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
        }


class TestSettings(BaseSettings):
    """测试配置"""

    batch_size: int = 100
    table_name: str = "test_users"

    model_config = SettingsConfigDict(env_prefix="TEST_", extra="ignore")

    @property
    def config_dict(self) -> dict:
        return {
            "batch_size": self.batch_size,
            "table_name": self.table_name,
        }


class Settings(BaseSettings):
    """主配置类"""

    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    log: LogSettings = LogSettings()
    llm: LLMSettings = LLMSettings()
    app: AppSettings = AppSettings()
    test: TestSettings = TestSettings()

    model_config = SettingsConfigDict(
        extra="ignore",  # 允许额外的字段
    )


# 创建全局配置实例
settings = Settings()
