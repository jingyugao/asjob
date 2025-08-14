from pydantic import BaseModel, Field
from typing import Optional


class ConnectorBase(BaseModel):
    """连接器基础模型"""

    name: str = Field(..., min_length=1, max_length=100, description="连接器名称")
    db_type: str = Field(..., description="数据库类型")
    host: str = Field(..., description="主机地址")
    port: int = Field(..., ge=1, le=65535, description="端口")
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    database: str = Field(..., description="数据库名")
    description: Optional[str] = Field(None, description="描述")
