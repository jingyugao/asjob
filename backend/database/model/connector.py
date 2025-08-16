from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ConnectorModel(BaseModel):
    """连接器数据模型（数据库层）"""

    id: Optional[int] = Field(None, description="主键ID")
    name: str = Field("", description="连接器名称")
    db_type: str = Field("", description="数据库类型")
    host: str = Field("", description="主机地址")
    port: int = Field(0, ge=0, description="端口")
    username: str = Field("", description="用户名")
    password: str = Field("", description="密码")
    database_name: str = Field("", description="数据库名")
    description: Optional[str] = Field(None, description="描述")
    is_active: bool = Field(True, description="是否激活")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    def __repr__(self) -> str:
        return f"<ConnectorModel(id={self.id}, name='{self.name}', db_type='{self.db_type}')>"

    @classmethod
    def from_dict(cls, data: dict) -> "ConnectorModel":
        """从字典创建模型实例"""
        if "database" in data:
            data["database_name"] = data.pop("database")
        return cls(**data)

    def to_dict(self) -> dict:
        """转换为字典（对外API使用`database`字段名）"""
        data = {
            "id": self.id,
            "name": self.name,
            "db_type": self.db_type,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "database": self.database_name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        return {key: value for key, value in data.items() if value is not None}

    class Config:
        from_attributes = True

    @property
    def database(self) -> str:
        """对外只读的 `database` 名称（映射到 `database_name`）。"""
        return self.database_name
