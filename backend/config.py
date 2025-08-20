import os
from typing import Optional


class Config:
    """统一配置管理类"""
    
    # 数据库配置
    @staticmethod
    def get_mysql_host() -> str:
        return os.getenv("MYSQL_HOST", "localhost")
    
    @staticmethod
    def get_mysql_port() -> int:
        return int(os.getenv("MYSQL_PORT", "3306"))
    
    @staticmethod
    def get_mysql_user() -> str:
        return os.getenv("MYSQL_USER", "root")
    
    @staticmethod
    def get_mysql_password() -> str:
        return os.getenv("MYSQL_PASSWORD", "password")
    
    @staticmethod
    def get_mysql_database() -> str:
        return os.getenv("MYSQL_DATABASE", "test_db")
    
    @staticmethod
    def get_mysql_config() -> dict:
        return {
            "host": Config.get_mysql_host(),
            "port": Config.get_mysql_port(),
            "username": Config.get_mysql_user(),
            "password": Config.get_mysql_password(),
            "database": Config.get_mysql_database(),
        }
    
    # Redis配置
    @staticmethod
    def get_redis_host() -> str:
        return os.getenv("REDIS_HOST", "localhost")
    
    @staticmethod
    def get_redis_port() -> int:
        return int(os.getenv("REDIS_PORT", "6379"))
    
    @staticmethod
    def get_redis_db() -> int:
        return int(os.getenv("REDIS_DB", "0"))
    
    @staticmethod
    def get_redis_config() -> dict:
        return {
            "host": Config.get_redis_host(),
            "port": Config.get_redis_port(),
            "db": Config.get_redis_db(),
        }
    
    # 日志配置
    @staticmethod
    def get_log_level() -> str:
        return os.getenv("LOG_LEVEL", "INFO").upper()
    
    @staticmethod
    def get_log_format() -> str:
        return "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    
    @staticmethod
    def get_log_date_format() -> str:
        return "%Y-%m-%d %H:%M:%S"
    
    # LLM配置
    @staticmethod
    def get_llm_model() -> str:
        return os.getenv("LLM_MODEL", "llama2")
    
    @staticmethod
    def get_llm_base_url() -> str:
        return os.getenv("LLM_BASE_URL", "http://localhost:11434")
    
    @staticmethod
    def get_llm_temperature() -> float:
        return float(os.getenv("LLM_TEMPERATURE", "0.7"))
    
    @staticmethod
    def get_llm_timeout() -> int:
        return int(os.getenv("LLM_TIMEOUT", "120"))
    
    @staticmethod
    def get_llm_config() -> dict:
        return {
            "model": Config.get_llm_model(),
            "base_url": Config.get_llm_base_url(),
            "temperature": Config.get_llm_temperature(),
            "timeout": Config.get_llm_timeout(),
        }
    
    # 应用配置
    @staticmethod
    def get_app_host() -> str:
        return os.getenv("APP_HOST", "0.0.0.0")
    
    @staticmethod
    def get_app_port() -> int:
        return int(os.getenv("APP_PORT", "8000"))
    
    @staticmethod
    def get_app_debug() -> bool:
        return os.getenv("APP_DEBUG", "false").lower() == "true"
    
    @staticmethod
    def get_app_config() -> dict:
        return {
            "host": Config.get_app_host(),
            "port": Config.get_app_port(),
            "debug": Config.get_app_debug(),
        }
    
    # 测试配置
    @staticmethod
    def get_test_batch_size() -> int:
        return int(os.getenv("TEST_BATCH_SIZE", "100"))
    
    @staticmethod
    def get_test_table_name() -> str:
        return os.getenv("TEST_TABLE_NAME", "test_users")
    
    @staticmethod
    def get_test_config() -> dict:
        return {
            "batch_size": Config.get_test_batch_size(),
            "table_name": Config.get_test_table_name(),
        }

# 兼容性配置（保持向后兼容）
MYSQL_CONFIG = Config.get_mysql_config()
REDIS_CONFIG = Config.get_redis_config()
TEST_CONFIG = Config.get_test_config()
