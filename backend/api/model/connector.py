from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ConnectorCreateReq(BaseModel):
    """创建连接器请求模型"""

    name: str = Field(..., min_length=1, max_length=100, description="连接器名称")
    db_type: str = Field(..., description="数据库类型")
    host: str = Field(..., description="主机地址")
    port: int = Field(..., ge=1, le=65535, description="端口")
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    database: str = Field(..., description="数据库名")
    description: Optional[str] = Field(None, description="描述")
    is_active: bool = Field(True, description="是否激活")


class ConnectorUpdateReq(BaseModel):
    """更新连接器请求模型"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="连接器名称"
    )
    db_type: Optional[str] = Field(None, description="数据库类型")
    host: Optional[str] = Field(None, description="主机地址")
    port: Optional[int] = Field(None, ge=1, le=65535, description="端口")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    database: Optional[str] = Field(None, description="数据库名")
    description: Optional[str] = Field(None, description="描述")
    is_active: Optional[bool] = Field(None, description="是否激活")


class ConnectorRsp(BaseModel):
    """连接器响应模型"""

    id: int
    name: str
    db_type: str
    host: str
    port: int
    username: str
    password: str
    database: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageRsp(BaseModel):
    message: str


class TestConnectorRsp(BaseModel):
    connected: bool


class StatsSummaryRsp(BaseModel):
    total: int
    mysql: int
    doris: int
    active: int
    inactive: int
