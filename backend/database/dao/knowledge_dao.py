from typing import List, Optional, Dict, Any
from pymysql.cursors import DictCursor
from backend.database.model.knowledge import KnowledgeModel


class KnowledgeDAO:
    """知识标注数据访问对象"""

    def __init__(self, cursor: DictCursor):
        self.cursor = cursor

    def create(self, knowledge_data: Dict[str, Any]) -> KnowledgeModel:
        """创建知识标注"""
        sql = """
        INSERT INTO knowledge (target_type, target_name, content, created_by)
        VALUES (%(target_type)s, %(target_name)s, %(content)s, %(created_by)s)
        """
        self.cursor.execute(sql, knowledge_data)
        new_id = self.cursor.lastrowid
        return self.get_by_id(new_id)

    def get_by_id(self, knowledge_id: int) -> Optional[KnowledgeModel]:
        sql = "SELECT * FROM knowledge WHERE id = %s"
        self.cursor.execute(sql, (knowledge_id,))
        result = self.cursor.fetchone()
        if result:
            return KnowledgeModel.model_validate(result)
        return None

    def list_by_target(
        self, target_type: str, target_name: str
    ) -> List[KnowledgeModel]:
        sql = "SELECT * FROM knowledge WHERE target_type = %s AND target_name = %s ORDER BY id DESC"
        self.cursor.execute(sql, (target_type, target_name))
        results = self.cursor.fetchall()
        return [KnowledgeModel.model_validate(row) for row in results]

    def list_by_prefix(
        self, target_type: str, target_prefix: str
    ) -> List[KnowledgeModel]:
        """按前缀查询（便于按库/表聚合查询）。"""
        sql = "SELECT * FROM knowledge WHERE target_type = %s AND target_name LIKE %s ORDER BY id DESC"
        self.cursor.execute(sql, (target_type, f"{target_prefix}%"))
        results = self.cursor.fetchall()
        return [KnowledgeModel.model_validate(row) for row in results]

    def update_content(
        self, knowledge_id: int, content: str
    ) -> Optional[KnowledgeModel]:
        sql = "UPDATE knowledge SET content = %s WHERE id = %s"
        self.cursor.execute(sql, (content, knowledge_id))
        return self.get_by_id(knowledge_id)

    def delete(self, knowledge_id: int) -> bool:
        sql = "DELETE FROM knowledge WHERE id = %s"
        self.cursor.execute(sql, (knowledge_id,))
        return self.cursor.rowcount > 0
