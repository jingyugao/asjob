from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ..dao.connector_dao import ConnectorDAO
from ..model.connector import ConnectorModel


class ConnectorService:
    """连接器服务层"""

    def __init__(self, session: Session):
        self.dao = ConnectorDAO(session)

    def create_connector(self, connector_data: Dict[str, Any]) -> ConnectorModel:
        """创建连接器"""
        # 检查名称是否已存在
        if self.dao.get_by_name(connector_data["name"]):
            raise ValueError(
                f"Connector with name '{connector_data['name']}' already exists"
            )

        return self.dao.create(connector_data)

    def get_connector(self, connector_id: int) -> Optional[ConnectorModel]:
        """获取连接器"""
        return self.dao.get_by_id(connector_id)

    def get_connector_by_name(self, name: str) -> Optional[ConnectorModel]:
        """根据名称获取连接器"""
        return self.dao.get_by_name(name)

    def list_connectors(self, skip: int = 0, limit: int = 100) -> List[ConnectorModel]:
        """列出连接器"""
        return self.dao.get_all(skip, limit)

    def list_active_connectors(self) -> List[ConnectorModel]:
        """列出激活的连接器"""
        return self.dao.get_active()

    def list_connectors_by_type(self, db_type: str) -> List[ConnectorModel]:
        """根据类型列出连接器"""
        return self.dao.get_by_type(db_type)

    def search_connectors(self, keyword: str) -> List[ConnectorModel]:
        """搜索连接器"""
        return self.dao.search(keyword)

    def update_connector(
        self, connector_id: int, update_data: Dict[str, Any]
    ) -> Optional[ConnectorModel]:
        """更新连接器"""
        # 如果更新名称，检查是否与其他连接器冲突
        if "name" in update_data:
            existing = self.dao.get_by_name(update_data["name"])
            if existing and existing.id != connector_id:
                raise ValueError(
                    f"Connector with name '{update_data['name']}' already exists"
                )

        return self.dao.update(connector_id, update_data)

    def delete_connector(self, connector_id: int) -> bool:
        """删除连接器"""
        return self.dao.delete(connector_id)

    def deactivate_connector(self, connector_id: int) -> bool:
        """停用连接器"""
        return self.dao.deactivate(connector_id)

    def activate_connector(self, connector_id: int) -> bool:
        """激活连接器"""
        return self.dao.activate(connector_id)

    def test_connector(self, connector_id: int) -> bool:
        """测试连接器连接"""
        return self.dao.test_connection(connector_id)

    def get_connector_stats(self) -> Dict[str, Any]:
        """获取连接器统计信息"""
        total = self.dao.count()
        mysql_count = self.dao.count_by_type("mysql")
        doris_count = self.dao.count_by_type("doris")
        active_count = len(self.dao.get_active())

        return {
            "total": total,
            "mysql": mysql_count,
            "doris": doris_count,
            "active": active_count,
            "inactive": total - active_count,
        }
