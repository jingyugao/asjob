import os

from pydantic import BaseModel
from backend.config import Config


class DatabaseConfig(BaseModel):
    """数据库配置"""

    # 数据库连接参数
    host: str
    port: int
    username: str
    password: str
    database: str

    def __init__(self, **data):
        # 从统一配置接口读取配置
        super().__init__(
            host=Config.get_mysql_host(),
            port=Config.get_mysql_port(),
            username=Config.get_mysql_user(),
            password=Config.get_mysql_password(),
            database=Config.get_mysql_database(),
        )

    @property
    def mysql_dns(self) -> str:
        """构建MySQL连接字符串"""
        if self.password:
            return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            return f"mysql://{self.username}@{self.host}:{self.port}/{self.database}"

    @property
    def url(self) -> str:
        """构建数据库连接URL"""
        return self.mysql_dns

    @property
    def connection_params(self) -> dict:
        """返回连接参数"""
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "database": self.database,
        }
