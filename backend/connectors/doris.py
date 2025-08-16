import pymysql
from typing import List, Dict, Any, Optional, Iterator
from contextlib import contextmanager
from .base import DatabaseConnector
from backend.logger import get_logger


class DorisConnector(DatabaseConnector):
    """Doris数据库连接器（使用MySQL协议）"""

    def __init__(
        self, host: str, port: int, username: str, password: str, database: str
    ):
        super().__init__(host, port, username, password, database)
        self.db_type = "doris"
        self.logger = get_logger("DorisConnector")

    def test_connection(self) -> bool:
        """测试Doris连接"""
        try:
            self.logger.info(
                f"Testing Doris connection to {self.host}:{self.port}/{self.database}"
            )
            with self.get_connection() as connection:
                connection.ping()
                self.logger.info("Doris connection test successful")
                return True
        except Exception as e:
            self.logger.error(f"Doris connection test failed: {str(e)}")
            return False

    def get_tables(self) -> List[str]:
        """获取所有表名"""
        try:
            self.logger.info(f"Getting tables from Doris database {self.database}")
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SHOW TABLES")
                    tables = [row[0] for row in cursor.fetchall()]
                    self.logger.info(
                        f"Retrieved {len(tables)} tables from Doris database"
                    )
                    return tables
        except Exception as e:
            self.logger.error(
                f"Failed to get tables from Doris database {self.database}: {str(e)}"
            )
            raise Exception(f"Failed to get tables: {str(e)}")

    def get_table_structure(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表结构"""
        try:
            self.logger.info(
                f"Getting table structure for '{table_name}' from Doris database {self.database}"
            )
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
                    self.logger.info(
                        f"Retrieved table structure for '{table_name}' with {len(columns)} columns"
                    )
                    return columns
        except Exception as e:
            self.logger.error(
                f"Failed to get table structure for '{table_name}' from Doris database {self.database}: {str(e)}"
            )
            raise Exception(f"Failed to get table structure: {str(e)}")

    def execute_query(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """执行SQL查询（返回完整结果）"""
        try:
            self.logger.info(f"Executing Doris query: {sql[:100]}...")
            with self.get_connection() as connection:
                with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                    if params:
                        cursor.execute(sql, params)
                    else:
                        cursor.execute(sql)
                    result = cursor.fetchall()
                    self.logger.info(
                        f"Doris query executed successfully, returned {len(result)} rows"
                    )
                    return result
        except Exception as e:
            self.logger.error(f"Failed to execute Doris query: {str(e)}")
            raise Exception(f"Failed to execute query: {str(e)}")

    def execute_query_iterator(
        self, sql: str, params: Optional[Dict[str, Any]] = None, batch_size: int = 1000
    ) -> Iterator[List[Dict[str, Any]]]:
        """执行SQL查询（返回迭代器，分批获取结果）"""
        try:
            self.logger.info(
                f"Executing Doris query with iterator: {sql[:100]}... (batch_size: {batch_size})"
            )
            with self.get_connection() as connection:
                with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                    if params:
                        cursor.execute(sql, params)
                    else:
                        cursor.execute(sql)

                    batch_count = 0
                    while True:
                        batch = cursor.fetchmany(batch_size)
                        if not batch:
                            break
                        batch_count += 1
                        yield batch

                    self.logger.info(
                        f"Doris query iterator completed, processed {batch_count} batches"
                    )
        except Exception as e:
            self.logger.error(f"Failed to execute Doris query with iterator: {str(e)}")
            raise Exception(f"Failed to execute query iterator: {str(e)}")

    def execute_update(self, sql: str, params: Optional[Dict[str, Any]] = None) -> int:
        """执行SQL更新操作"""
        try:
            self.logger.info(f"Executing Doris update: {sql[:100]}...")
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    if params:
                        cursor.execute(sql, params)
                    else:
                        cursor.execute(sql)
                    connection.commit()
                    row_count = cursor.rowcount
                    self.logger.info(
                        f"Doris update executed successfully, affected {row_count} rows"
                    )
                    return row_count
        except Exception as e:
            self.logger.error(f"Failed to execute Doris update: {str(e)}")
            raise Exception(f"Failed to execute update: {str(e)}")

    def get_table_data(
        self, table_name: str, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """获取表数据"""
        sql = f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"
        self.logger.info(
            f"Getting table data from '{table_name}' (limit: {limit}, offset: {offset})"
        )
        return self.execute_query(sql)

    def get_table_data_iterator(
        self, table_name: str, batch_size: int = 1000
    ) -> Iterator[List[Dict[str, Any]]]:
        """获取表数据（返回迭代器，分批获取）"""
        sql = f"SELECT * FROM {table_name}"
        self.logger.info(
            f"Getting table data iterator from '{table_name}' (batch_size: {batch_size})"
        )
        return self.execute_query_iterator(sql, batch_size=batch_size)

    def get_table_count(self, table_name: str) -> int:
        """获取表记录数"""
        try:
            self.logger.info(
                f"Getting table count for '{table_name}' from Doris database {self.database}"
            )
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                    result = cursor.fetchone()
                    count = result[0] if result else 0
                    self.logger.info(f"Table '{table_name}' has {count} rows")
                    return count
        except Exception as e:
            self.logger.error(
                f"Failed to get table count for '{table_name}' from Doris database {self.database}: {str(e)}"
            )
            raise Exception(f"Failed to get table count: {str(e)}")

    @contextmanager
    def get_connection(self):
        """获取Doris连接的上下文管理器"""
        connection = None
        try:
            self.logger.debug(
                f"Creating Doris connection to {self.host}:{self.port}/{self.database}"
            )
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database=self.database,
                charset="utf8mb4",
                autocommit=False,
            )
            yield connection
        except Exception as e:
            self.logger.error(f"Failed to create Doris connection: {str(e)}")
            raise
        finally:
            if connection:
                try:
                    connection.close()
                    self.logger.debug("Doris connection closed")
                except Exception as e:
                    self.logger.warning(f"Error closing Doris connection: {str(e)}")
