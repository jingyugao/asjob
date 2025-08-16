from typing import List, Optional, Dict, Any
from pymysql.cursors import DictCursor
from backend.database.model.connector import ConnectorModel


class ConnectorDAO:
    """连接器数据访问对象"""

    def __init__(self, cursor: DictCursor):
        self.cursor = cursor

    def create(self, connector_data: Dict[str, Any]) -> ConnectorModel:
        """创建连接器"""
        # 处理字段名映射
        if "database" in connector_data:
            connector_data["database_name"] = connector_data.pop("database")

        sql = """
        INSERT INTO connectors (name, db_type, host, port, username, password, database_name, description, is_active)
        VALUES (%(name)s, %(db_type)s, %(host)s, %(port)s, %(username)s, %(password)s, %(database_name)s, %(description)s, %(is_active)s)
        """

        self.cursor.execute(sql, connector_data)
        connector_id = self.cursor.lastrowid

        # 获取创建的连接器
        return self.get_by_id(connector_id)

    def get_by_id(self, connector_id: int) -> Optional[ConnectorModel]:
        """根据ID获取连接器"""
        sql = "SELECT * FROM connectors WHERE id = %s"
        self.cursor.execute(sql, (connector_id,))
        result = self.cursor.fetchone()

        if result:
            return ConnectorModel.from_dict(result)
        return None

    def get_by_name(self, name: str) -> Optional[ConnectorModel]:
        """根据名称获取连接器"""
        sql = "SELECT * FROM connectors WHERE name = %s"
        self.cursor.execute(sql, (name,))
        result = self.cursor.fetchone()

        if result:
            return ConnectorModel.from_dict(result)
        return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ConnectorModel]:
        """获取所有连接器"""
        sql = "SELECT * FROM connectors ORDER BY id LIMIT %s OFFSET %s"
        self.cursor.execute(sql, (limit, skip))
        results = self.cursor.fetchall()

        return [ConnectorModel.from_dict(result) for result in results]

    def get_active(self) -> List[ConnectorModel]:
        """获取所有激活的连接器"""
        sql = "SELECT * FROM connectors WHERE is_active = TRUE ORDER BY id"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        return [ConnectorModel.from_dict(result) for result in results]

    def get_by_type(self, db_type: str) -> List[ConnectorModel]:
        """根据数据库类型获取连接器"""
        sql = "SELECT * FROM connectors WHERE db_type = %s ORDER BY id"
        self.cursor.execute(sql, (db_type,))
        results = self.cursor.fetchall()

        return [ConnectorModel.from_dict(result) for result in results]

    def search(self, keyword: str) -> List[ConnectorModel]:
        """搜索连接器"""
        sql = """
        SELECT * FROM connectors 
        WHERE name LIKE %s OR host LIKE %s OR database_name LIKE %s OR description LIKE %s
        ORDER BY id
        """
        search_pattern = f"%{keyword}%"
        self.cursor.execute(
            sql, (search_pattern, search_pattern, search_pattern, search_pattern)
        )
        results = self.cursor.fetchall()

        return [ConnectorModel.from_dict(result) for result in results]

    def update(
        self, connector_id: int, update_data: Dict[str, Any]
    ) -> Optional[ConnectorModel]:
        """更新连接器"""
        # 处理字段名映射
        if "database" in update_data:
            update_data["database_name"] = update_data.pop("database")

        # 构建更新SQL
        set_clauses = []
        values = []
        for key, value in update_data.items():
            if hasattr(ConnectorModel, key):
                set_clauses.append(f"{key} = %s")
                values.append(value)

        if not set_clauses:
            return self.get_by_id(connector_id)

        sql = f"UPDATE connectors SET {', '.join(set_clauses)} WHERE id = %s"
        values.append(connector_id)

        self.cursor.execute(sql, values)

        return self.get_by_id(connector_id)

    def delete(self, connector_id: int) -> bool:
        """删除连接器"""
        sql = "DELETE FROM connectors WHERE id = %s"
        self.cursor.execute(sql, (connector_id,))

        return self.cursor.rowcount > 0

    def deactivate(self, connector_id: int) -> bool:
        """停用连接器"""
        sql = "UPDATE connectors SET is_active = FALSE WHERE id = %s"
        self.cursor.execute(sql, (connector_id,))

        return self.cursor.rowcount > 0

    def activate(self, connector_id: int) -> bool:
        """激活连接器"""
        sql = "UPDATE connectors SET is_active = TRUE WHERE id = %s"
        self.cursor.execute(sql, (connector_id,))

        return self.cursor.rowcount > 0

    def test_connection(self, connector_id: int) -> bool:
        """测试连接器连接"""
        connector = self.get_by_id(connector_id)
        if not connector:
            return False

        try:
            from backend.infra.connectors import get_connector_instance

            connector_instance = get_connector_instance(
                db_type=connector.db_type,
                host=connector.host,
                port=connector.port,
                username=connector.username,
                password=connector.password,
                database=connector.database_name,
            )
            return connector_instance.test_connection()
        except Exception:
            return False

    def count(self) -> int:
        """获取连接器总数"""
        sql = "SELECT COUNT(*) as count FROM connectors"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()

        return result["count"] if result else 0

    def count_by_type(self, db_type: str) -> int:
        """根据类型统计连接器数量"""
        sql = "SELECT COUNT(*) as count FROM connectors WHERE db_type = %s"
        self.cursor.execute(sql, (db_type,))
        result = self.cursor.fetchone()

        return result["count"] if result else 0
