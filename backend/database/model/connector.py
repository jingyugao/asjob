from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ConnectorModel:
    """连接器数据模型"""
    
    id: Optional[int] = None
    name: str = ""
    db_type: str = ""
    host: str = ""
    port: int = 0
    username: str = ""
    password: str = ""
    database_name: str = ""
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __repr__(self):
        return f"<ConnectorModel(id={self.id}, name='{self.name}', db_type='{self.db_type}')>"
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConnectorModel':
        """从字典创建模型实例"""
        # 处理字段名映射
        if 'database' in data:
            data['database_name'] = data.pop('database')
        
        return cls(**data)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'db_type': self.db_type,
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'database': self.database_name,  # 保持API兼容性
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        return {k: v for k, v in data.items() if v is not None}
