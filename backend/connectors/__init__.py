from .base import DatabaseConnector
from .mysql import MySQLConnector
from .doris import DorisConnector

__all__ = ["DatabaseConnector", "MySQLConnector", "DorisConnector"]


def get_connector_instance(
    db_type: str, host: str, port: int, username: str, password: str, database: str
) -> DatabaseConnector:
    """根据数据库类型创建连接器实例"""
    if db_type.lower() == "mysql":
        return MySQLConnector(host, port, username, password, database)
    elif db_type.lower() == "doris":
        return DorisConnector(host, port, username, password, database)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
