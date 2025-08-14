from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..model.connector import ConnectorModel


class ConnectorDAO:
    """连接器数据访问对象"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, connector_data: Dict[str, Any]) -> ConnectorModel:
        """创建连接器"""
        connector = ConnectorModel(**connector_data)
        self.session.add(connector)
        self.session.commit()
        self.session.refresh(connector)
        return connector

    def get_by_id(self, connector_id: int) -> Optional[ConnectorModel]:
        """根据ID获取连接器"""
        return (
            self.session.query(ConnectorModel)
            .filter(ConnectorModel.id == connector_id)
            .first()
        )

    def get_by_name(self, name: str) -> Optional[ConnectorModel]:
        """根据名称获取连接器"""
        return (
            self.session.query(ConnectorModel)
            .filter(ConnectorModel.name == name)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ConnectorModel]:
        """获取所有连接器"""
        return self.session.query(ConnectorModel).offset(skip).limit(limit).all()

    def get_active(self) -> List[ConnectorModel]:
        """获取所有激活的连接器"""
        return (
            self.session.query(ConnectorModel)
            .filter(ConnectorModel.is_active == True)
            .all()
        )

    def get_by_type(self, db_type: str) -> List[ConnectorModel]:
        """根据数据库类型获取连接器"""
        return (
            self.session.query(ConnectorModel)
            .filter(ConnectorModel.db_type == db_type)
            .all()
        )

    def search(self, keyword: str) -> List[ConnectorModel]:
        """搜索连接器"""
        return (
            self.session.query(ConnectorModel)
            .filter(
                or_(
                    ConnectorModel.name.contains(keyword),
                    ConnectorModel.host.contains(keyword),
                    ConnectorModel.database.contains(keyword),
                    ConnectorModel.description.contains(keyword),
                )
            )
            .all()
        )

    def update(
        self, connector_id: int, update_data: Dict[str, Any]
    ) -> Optional[ConnectorModel]:
        """更新连接器"""
        connector = self.get_by_id(connector_id)
        if connector:
            for key, value in update_data.items():
                if hasattr(connector, key):
                    setattr(connector, key, value)
            self.session.commit()
            self.session.refresh(connector)
        return connector

    def delete(self, connector_id: int) -> bool:
        """删除连接器"""
        connector = self.get_by_id(connector_id)
        if connector:
            self.session.delete(connector)
            self.session.commit()
            return True
        return False

    def deactivate(self, connector_id: int) -> bool:
        """停用连接器"""
        connector = self.get_by_id(connector_id)
        if connector:
            connector.is_active = False
            self.session.commit()
            return True
        return False

    def activate(self, connector_id: int) -> bool:
        """激活连接器"""
        connector = self.get_by_id(connector_id)
        if connector:
            connector.is_active = True
            self.session.commit()
            return True
        return False

    def test_connection(self, connector_id: int) -> bool:
        """测试连接器连接"""
        connector = self.get_by_id(connector_id)
        if not connector:
            return False

        try:
            from ...connectors import get_connector_instance

            connector_instance = get_connector_instance(
                db_type=connector.db_type,
                host=connector.host,
                port=connector.port,
                username=connector.username,
                password=connector.password,
                database=connector.database,
            )
            return connector_instance.test_connection()
        except Exception:
            return False

    def count(self) -> int:
        """获取连接器总数"""
        return self.session.query(ConnectorModel).count()

    def count_by_type(self, db_type: str) -> int:
        """根据类型统计连接器数量"""
        return (
            self.session.query(ConnectorModel)
            .filter(ConnectorModel.db_type == db_type)
            .count()
        )
