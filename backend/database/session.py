import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from typing import Generator
from .config import DatabaseConfig

config = DatabaseConfig()

class DatabaseConnection:
    """数据库连接管理类"""
    
    def __init__(self):
        self.connection_params = config.connection_params
    
    def get_connection(self):
        """获取数据库连接"""
        return pymysql.connect(
            host=self.connection_params["host"],
            port=self.connection_params["port"],
            user=self.connection_params["username"],
            password=self.connection_params["password"],
            database=self.connection_params["database"],
            charset='utf8mb4',
            cursorclass=DictCursor,
            autocommit=False
        )
    
    @contextmanager
    def get_cursor(self) -> Generator[pymysql.cursors.DictCursor, None, None]:
        """获取数据库游标的上下文管理器"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

# 全局数据库连接实例
db_connection = DatabaseConnection()

def get_db_cursor():
    """获取数据库游标的依赖注入函数"""
    with db_connection.get_cursor() as cursor:
        yield cursor

def create_tables():
    """创建所有表"""
    create_connectors_table = """
    CREATE TABLE IF NOT EXISTS connectors (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE COMMENT '连接器名称',
        db_type VARCHAR(50) NOT NULL COMMENT '数据库类型',
        host VARCHAR(255) NOT NULL COMMENT '主机地址',
        port INT NOT NULL COMMENT '端口',
        username VARCHAR(100) NOT NULL COMMENT '用户名',
        password VARCHAR(255) NOT NULL COMMENT '密码',
        database_name VARCHAR(100) NOT NULL COMMENT '数据库名',
        description TEXT COMMENT '描述',
        is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    with db_connection.get_cursor() as cursor:
        cursor.execute(create_connectors_table)

def get_connection_info():
    """获取连接信息（用于调试）"""
    return {
        "mysql_dns": config.mysql_dns,
        "connection_params": config.connection_params,
    }
