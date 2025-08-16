from typing import List, Optional
from pymysql.cursors import DictCursor
from backend.database.model.knowledge import KnowledgeModel
from backend.database.dao.knowledge_dao import KnowledgeDAO
import logging


class KnowledgeService:
    """知识标注服务层"""

    def __init__(self, cursor: DictCursor):
        self.dao = KnowledgeDAO(cursor)
        self.logger = logging.getLogger("KnowledgeService")

    def create_knowledge(self, data: dict) -> KnowledgeModel:
        self._validate_target(data.get("target_type"), data.get("target_name"))
        self.logger.info(
            f"Creating knowledge for {data.get('target_type')}:{data.get('target_name')}"
        )
        return self.dao.create(data)

    def get_knowledge(self, knowledge_id: int) -> Optional[KnowledgeModel]:
        return self.dao.get_by_id(knowledge_id)

    def list_for_target(
        self, target_type: str, target_name: str
    ) -> List[KnowledgeModel]:
        self._validate_target(target_type, target_name)
        return self.dao.list_by_target(target_type, target_name)

    def list_by_prefix(
        self, target_type: str, target_prefix: str
    ) -> List[KnowledgeModel]:
        return self.dao.list_by_prefix(target_type, target_prefix)

    def update_content(
        self, knowledge_id: int, content: str
    ) -> Optional[KnowledgeModel]:
        return self.dao.update_content(knowledge_id, content)

    def delete(self, knowledge_id: int) -> bool:
        return self.dao.delete(knowledge_id)

    def _validate_target(
        self, target_type: Optional[str], target_name: Optional[str]
    ) -> None:
        if not target_type or target_type not in {"database", "table", "field"}:
            raise ValueError("target_type 必须为 'database' | 'table' | 'field'")
        if not target_name:
            raise ValueError("target_name 不能为空")
        parts = target_name.split("::")
        if target_type == "database" and len(parts) != 2:
            raise ValueError("database 级别的 target_name 必须为 'connector::db'")
        if target_type == "table" and len(parts) != 3:
            raise ValueError("table 级别的 target_name 必须为 'connector::db::table'")
        if target_type == "field" and len(parts) != 4:
            raise ValueError(
                "field 级别的 target_name 必须为 'connector::db::table::field'"
            )
