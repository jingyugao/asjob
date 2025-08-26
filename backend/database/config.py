import os

from pydantic import BaseModel

from backend.config import settings

# 数据库连接配置
DATABASE_CONFIG = {
    "host": settings.database.host,
    "port": settings.database.port,
    "username": settings.database.user,
    "password": settings.database.password,
    "database": settings.database.database,
}
