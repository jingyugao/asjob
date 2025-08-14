from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from ..session import Base


class ConnectorModel(Base):
    """连接器数据模型"""

    __tablename__ = "connectors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, comment="连接器名称")
    db_type = Column(String(50), nullable=False, comment="数据库类型")
    host = Column(String(255), nullable=False, comment="主机地址")
    port = Column(Integer, nullable=False, comment="端口")
    username = Column(String(100), nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    database = Column(String(100), nullable=False, comment="数据库名")
    description = Column(Text, comment="描述")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), comment="更新时间"
    )

    def __repr__(self):
        return f"<ConnectorModel(id={self.id}, name='{self.name}', db_type='{self.db_type}')>"
