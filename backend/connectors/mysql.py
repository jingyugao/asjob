import pymysql
from typing import List, Dict, Any, Optional, Iterator
from contextlib import contextmanager
from .base import DatabaseConnector


class MySQLConnector(DatabaseConnector):
    """MySQL数据库连接器"""

    def __init__(
        self, host: str, port: int, username: str, password: str, database: str
    ):
        super().__init__(host, port, username, password, database)
        self.db_type = "mysql"

    def test_connection(self) -> bool:
        """测试MySQL连接"""
        try:
            with self.get_connection() as connection:
                connection.ping()
                return True
        except Exception:
            return False

    def get_tables(self) -> List[str]:
        """获取所有表名"""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SHOW TABLES")
                    return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            raise Exception(f"Failed to get tables: {str(e)}")

    def get_table_structure(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表结构"""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"DESCRIBE {table_name}")
                    columns = []
                    for row in cursor.fetchall():
                        columns.append(
                            {
                                "field": row[0],
                                "type": row[1],
                                "null": row[2],
                                "key": row[3],
                                "default": row[4],
                                "extra": row[5],
                            }
                        )
                    return columns
        except Exception as e:
            raise Exception(f"Failed to get table structure: {str(e)}")

    def execute_query(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """执行SQL查询（返回完整结果）"""
        try:
            with self.get_connection() as connection:
                with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                    if params:
                        cursor.execute(sql, params)
                    else:
                        cursor.execute(sql)
                    return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Failed to execute query: {str(e)}")

    def execute_query_iterator(
        self, sql: str, params: Optional[Dict[str, Any]] = None, batch_size: int = 1000
    ) -> Iterator[List[Dict[str, Any]]]:
        """执行SQL查询（返回迭代器，分批获取结果）"""
        try:
            with self.get_connection() as connection:
                with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                    if params:
                        cursor.execute(sql, params)
                    else:
                        cursor.execute(sql)

                    while True:
                        batch = cursor.fetchmany(batch_size)
                        if not batch:
                            break
                        yield batch
        except Exception as e:
            raise Exception(f"Failed to execute query iterator: {str(e)}")

    def execute_update(self, sql: str, params: Optional[Dict[str, Any]] = None) -> int:
        """执行SQL更新操作"""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    if params:
                        cursor.execute(sql, params)
                    else:
                        cursor.execute(sql)
                    connection.commit()
                    return cursor.rowcount
        except Exception as e:
            raise Exception(f"Failed to execute update: {str(e)}")

    def get_table_data(
        self, table_name: str, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """获取表数据"""
        sql = f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"
        return self.execute_query(sql)

    def get_table_data_iterator(
        self, table_name: str, batch_size: int = 1000
    ) -> Iterator[List[Dict[str, Any]]]:
        """获取表数据（返回迭代器，分批获取）"""
        sql = f"SELECT * FROM {table_name}"
        return self.execute_query_iterator(sql, batch_size=batch_size)

    def get_table_count(self, table_name: str) -> int:
        """获取表记录数"""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                    result = cursor.fetchone()
                    return result[0] if result else 0
        except Exception as e:
            raise Exception(f"Failed to get table count: {str(e)}")

    @contextmanager
    def get_connection(self):
        """获取MySQL连接的上下文管理器"""
        connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            database=self.database,
            charset="utf8mb4",
            autocommit=False,
        )
        try:
            yield connection
        finally:
            connection.close()
