from pydantic_settings import BaseSettings
from pydantic import validator
from typing import Optional
import urllib.parse


class DatabaseConfig(BaseSettings):
    """数据库配置"""

    # 连接字符串配置
    mysql_dns: str = "mysql://root:@localhost:3306/asjob"

    # 兼容性配置（可选）
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None

    @validator("mysql_dns")
    def validate_mysql_dns(cls, v):
        """验证MySQL连接字符串格式"""
        if not v.startswith("mysql://"):
            raise ValueError("MySQL DNS must start with mysql://")
        return v

    @property
    def url(self) -> str:
        """构建数据库连接URL"""
        # 如果提供了完整的连接字符串，直接使用
        if self.mysql_dns:
            # 确保连接字符串包含数据库名
            if "/asjob" not in self.mysql_dns:
                # 如果没有数据库名，添加默认数据库
                if self.mysql_dns.endswith("/"):
                    return f"{self.mysql_dns}asjob"
                else:
                    return f"{self.mysql_dns}/asjob"
            return self.mysql_dns

        # 兼容性：使用单独的配置项构建URL
        password_part = f":{self.password}" if self.password else ""
        return f"mysql+pymysql://{self.username}{password_part}@{self.host}:{self.port}/{self.database}"

    @property
    def connection_params(self) -> dict:
        """解析连接字符串，返回连接参数"""
        if not self.mysql_dns:
            return {}

        # 使用urllib.parse来正确解析连接字符串
        try:
            # 解析连接字符串
            parsed = urllib.parse.urlparse(self.mysql_dns)

            # 提取用户名和密码
            username = parsed.username or ""
            password = parsed.password or ""

            # 提取主机和端口
            host = parsed.hostname or ""
            port = parsed.port or 3306

            # 提取数据库名
            database = parsed.path.lstrip("/") or "asjob"

            return {
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "database": database,
            }
        except Exception as e:
            raise ValueError(f"Invalid MySQL DNS format: {e}")

    class Config:
        env_prefix = "DB_"
