from typing import List, Optional, Dict, Any
from pymysql.cursors import DictCursor
from backend.database.dao.connector_dao import ConnectorDAO
from backend.database.model.connector import ConnectorModel
from backend.logger import get_logger


class ConnectorService:
    """连接器服务层"""

    def __init__(self, cursor: DictCursor):
        self.dao = ConnectorDAO(cursor)
        self.logger = get_logger("ConnectorService")

    def create_connector(self, connector_data: Dict[str, Any]) -> ConnectorModel:
        """创建连接器"""
        try:
            self.logger.info(
                f"Creating connector: {connector_data['name']} ({connector_data['db_type']})"
            )

            # 检查名称是否已存在
            if self.dao.get_by_name(connector_data["name"]):
                error_msg = (
                    f"Connector with name '{connector_data['name']}' already exists"
                )
                self.logger.warning(error_msg)
                raise ValueError(error_msg)

            result = self.dao.create(connector_data)
            self.logger.info(
                f"Connector '{connector_data['name']}' created successfully with ID {result.id}"
            )
            return result
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(
                f"Failed to create connector '{connector_data['name']}': {str(e)}"
            )
            raise

    def get_connector(self, connector_id: int) -> Optional[ConnectorModel]:
        """获取连接器"""
        try:
            self.logger.info(f"Getting connector with ID: {connector_id}")
            connector = self.dao.get_by_id(connector_id)
            if connector:
                self.logger.info(
                    f"Retrieved connector '{connector.name}' (ID: {connector_id})"
                )
            else:
                self.logger.warning(f"Connector with ID {connector_id} not found")
            return connector
        except Exception as e:
            self.logger.error(
                f"Failed to get connector with ID {connector_id}: {str(e)}"
            )
            raise

    def get_connector_by_name(self, name: str) -> Optional[ConnectorModel]:
        """根据名称获取连接器"""
        try:
            self.logger.info(f"Getting connector by name: {name}")
            connector = self.dao.get_by_name(name)
            if connector:
                self.logger.info(f"Retrieved connector '{name}' (ID: {connector.id})")
            else:
                self.logger.warning(f"Connector with name '{name}' not found")
            return connector
        except Exception as e:
            self.logger.error(f"Failed to get connector by name '{name}': {str(e)}")
            raise

    def list_connectors(self, skip: int = 0, limit: int = 100) -> List[ConnectorModel]:
        """列出连接器"""
        try:
            self.logger.info(f"Listing connectors (skip: {skip}, limit: {limit})")
            connectors = self.dao.get_all(skip, limit)
            self.logger.info(f"Retrieved {len(connectors)} connectors")
            return connectors
        except Exception as e:
            self.logger.error(f"Failed to list connectors: {str(e)}")
            raise

    def list_active_connectors(self) -> List[ConnectorModel]:
        """列出激活的连接器"""
        try:
            self.logger.info("Listing active connectors")
            connectors = self.dao.get_active()
            self.logger.info(f"Retrieved {len(connectors)} active connectors")
            return connectors
        except Exception as e:
            self.logger.error(f"Failed to list active connectors: {str(e)}")
            raise

    def list_connectors_by_type(self, db_type: str) -> List[ConnectorModel]:
        """根据类型列出连接器"""
        try:
            self.logger.info(f"Listing connectors by type: {db_type}")
            connectors = self.dao.get_by_type(db_type)
            self.logger.info(
                f"Retrieved {len(connectors)} connectors of type '{db_type}'"
            )
            return connectors
        except Exception as e:
            self.logger.error(
                f"Failed to list connectors by type '{db_type}': {str(e)}"
            )
            raise

    def search_connectors(self, keyword: str) -> List[ConnectorModel]:
        """搜索连接器"""
        try:
            self.logger.info(f"Searching connectors with keyword: {keyword}")
            connectors = self.dao.search(keyword)
            self.logger.info(
                f"Found {len(connectors)} connectors matching keyword '{keyword}'"
            )
            return connectors
        except Exception as e:
            self.logger.error(
                f"Failed to search connectors with keyword '{keyword}': {str(e)}"
            )
            raise

    def update_connector(
        self, connector_id: int, update_data: Dict[str, Any]
    ) -> Optional[ConnectorModel]:
        """更新连接器"""
        try:
            self.logger.info(f"Updating connector with ID: {connector_id}")

            # 如果更新名称，检查是否与其他连接器冲突
            if "name" in update_data:
                existing = self.dao.get_by_name(update_data["name"])
                if existing and existing.id != connector_id:
                    error_msg = (
                        f"Connector with name '{update_data['name']}' already exists"
                    )
                    self.logger.warning(error_msg)
                    raise ValueError(error_msg)

            updated = self.dao.update(connector_id, update_data)
            if updated:
                self.logger.info(
                    f"Connector '{updated.name}' (ID: {connector_id}) updated successfully"
                )
            else:
                self.logger.warning(
                    f"Connector with ID {connector_id} not found for update"
                )
            return updated
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to update connector {connector_id}: {str(e)}")
            raise

    def delete_connector(self, connector_id: int) -> bool:
        """删除连接器"""
        try:
            self.logger.info(f"Deleting connector with ID: {connector_id}")
            result = self.dao.delete(connector_id)
            if result:
                self.logger.info(
                    f"Connector with ID {connector_id} deleted successfully"
                )
            else:
                self.logger.warning(
                    f"Connector with ID {connector_id} not found for deletion"
                )
            return result
        except Exception as e:
            self.logger.error(f"Failed to delete connector {connector_id}: {str(e)}")
            raise

    def deactivate_connector(self, connector_id: int) -> bool:
        """停用连接器"""
        try:
            self.logger.info(f"Deactivating connector with ID: {connector_id}")
            result = self.dao.deactivate(connector_id)
            if result:
                self.logger.info(
                    f"Connector with ID {connector_id} deactivated successfully"
                )
            else:
                self.logger.warning(
                    f"Connector with ID {connector_id} not found for deactivation"
                )
            return result
        except Exception as e:
            self.logger.error(
                f"Failed to deactivate connector {connector_id}: {str(e)}"
            )
            raise

    def activate_connector(self, connector_id: int) -> bool:
        """激活连接器"""
        try:
            self.logger.info(f"Activating connector with ID: {connector_id}")
            result = self.dao.activate(connector_id)
            if result:
                self.logger.info(
                    f"Connector with ID {connector_id} activated successfully"
                )
            else:
                self.logger.warning(
                    f"Connector with ID {connector_id} not found for activation"
                )
            return result
        except Exception as e:
            self.logger.error(f"Failed to activate connector {connector_id}: {str(e)}")
            raise

    def test_connector(self, connector_id: int) -> bool:
        """测试连接器连接"""
        try:
            self.logger.info(f"Testing connector with ID: {connector_id}")
            result = self.dao.test_connection(connector_id)
            self.logger.info(
                f"Connector {connector_id} test result: {'connected' if result else 'disconnected'}"
            )
            return result
        except Exception as e:
            self.logger.error(f"Failed to test connector {connector_id}: {str(e)}")
            raise

    def get_connector_stats(self) -> Dict[str, Any]:
        """获取连接器统计信息"""
        try:
            self.logger.info("Getting connector statistics")
            total = self.dao.count()
            mysql_count = self.dao.count_by_type("mysql")
            doris_count = self.dao.count_by_type("doris")
            active_count = len(self.dao.get_active())

            stats = {
                "total": total,
                "mysql": mysql_count,
                "doris": doris_count,
                "active": active_count,
                "inactive": total - active_count,
            }

            self.logger.info(f"Connector statistics: {stats}")
            return stats
        except Exception as e:
            self.logger.error(f"Failed to get connector statistics: {str(e)}")
            raise
