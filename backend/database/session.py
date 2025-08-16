import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from typing import Generator
import time
from .config import DatabaseConfig
import logging


config = DatabaseConfig()
logger = logging.getLogger("database.session")


class DatabaseConnection:
    """数据库连接管理类"""

    def __init__(self):
        self.connection_params = config.connection_params
        # 记录连接参数（注意生产环境不要记录密码）
        logger.debug(
            "准备建立MySQL连接",
            extra={
                "host": self.connection_params["host"],
                "port": self.connection_params["port"],
                "username": self.connection_params["username"],
                "database": self.connection_params["database"],
            },
        )

    def get_connection(self):
        """获取数据库连接"""
        try:
            logger.info(
                "正在建立MySQL数据库连接...",
                extra={
                    "host": self.connection_params["host"],
                    "port": self.connection_params["port"],
                    "username": self.connection_params["username"],
                    "database": self.connection_params["database"],
                },
            )

            conn = pymysql.connect(
                host=self.connection_params["host"],
                port=self.connection_params["port"],
                user=self.connection_params["username"],
                password=self.connection_params["password"],
                database=self.connection_params["database"],
                charset="utf8mb4",
                cursorclass=DictCursor,
                autocommit=False,
            )

            # 测试连接
            conn.ping(reconnect=False)

            # 记录连接成功信息
            logger.info(
                "MySQL连接建立成功",
                extra={
                    "connection_id": conn.thread_id(),
                    "server_version": getattr(conn, "server_version", None),
                    "charset": getattr(conn, "charset", None),
                    "autocommit": conn.autocommit(),
                    "host": self.connection_params["host"],
                    "port": self.connection_params["port"],
                    "username": self.connection_params["username"],
                    "database": self.connection_params["database"],
                },
            )

            return conn

        except Exception as e:
            # 记录连接失败信息（不记录密码）
            logger.exception(
                "MySQL连接失败",
                extra={
                    "host": self.connection_params["host"],
                    "port": self.connection_params["port"],
                    "username": self.connection_params["username"],
                    "database": self.connection_params["database"],
                },
            )
            raise

    @contextmanager
    def get_cursor(self) -> Generator[pymysql.cursors.DictCursor, None, None]:
        """获取数据库游标的上下文管理器"""
        conn = None
        cursor = None
        start_time = time.time()

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            logger.debug(
                "数据库游标创建成功",
                extra={
                    "connection_id": conn.thread_id(),
                    "cursor_type": type(cursor).__name__,
                },
            )

            yield cursor

            # 记录事务提交
            conn.commit()
            logger.debug(
                "事务提交成功",
                extra={"connection_id": conn.thread_id()},
            )

        except Exception as e:
            if conn:
                conn.rollback()
                logger.warning(
                    "事务回滚",
                    extra={"connection_id": conn.thread_id()},
                )
                logger.error(
                    "数据库事务回滚",
                    extra={
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "connection_id": conn.thread_id() if conn else None,
                    },
                )
            raise
        finally:
            execution_time = time.time() - start_time
            logger.debug(
                f"数据库操作完成，耗时: {execution_time:.3f}秒",
                extra={
                    "execution_time_seconds": execution_time,
                    "connection_id": conn.thread_id() if conn else None,
                },
            )

            if cursor:
                cursor.close()
                logger.debug("数据库游标已关闭")
            if conn:
                conn.close()
                logger.debug(
                    "连接关闭",
                    extra={"connection_id": conn.thread_id()},
                )
                logger.debug(
                    "数据库连接已关闭",
                    extra={"connection_id": conn.thread_id() if conn else None},
                )


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
