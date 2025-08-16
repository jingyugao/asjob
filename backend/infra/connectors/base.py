from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Iterator
from contextlib import contextmanager


class DatabaseConnector(ABC):
    """数据库连接器抽象基类"""

    def __init__(
        self, host: str, port: int, username: str, password: str, database: str
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database

    @abstractmethod
    def test_connection(self) -> bool:
        """测试数据库连接"""
        pass

    @abstractmethod
    def get_tables(self) -> List[str]:
        """获取所有表名"""
        pass

    @abstractmethod
    def get_table_structure(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表结构"""
        pass

    @abstractmethod
    def execute_query(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """执行SQL查询（返回完整结果）"""
        pass

    @abstractmethod
    def execute_query_iterator(
        self, sql: str, params: Optional[Dict[str, Any]] = None, batch_size: int = 1000
    ) -> Iterator[List[Dict[str, Any]]]:
        """执行SQL查询（返回迭代器，分批获取结果）"""
        pass

    @abstractmethod
    def execute_update(self, sql: str, params: Optional[Dict[str, Any]] = None) -> int:
        """执行SQL更新操作，返回影响行数"""
        pass

    @abstractmethod
    def get_table_data(
        self, table_name: str, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """获取表数据"""
        pass

    @abstractmethod
    def get_table_data_iterator(
        self, table_name: str, batch_size: int = 1000
    ) -> Iterator[List[Dict[str, Any]]]:
        """获取表数据（返回迭代器，分批获取）"""
        pass

    @abstractmethod
    def get_table_count(self, table_name: str) -> int:
        """获取表记录数"""
        pass

    @contextmanager
    @abstractmethod
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        pass
