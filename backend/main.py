import logging
import sys
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.api import api_router
from backend.config import settings
from backend.infra.connectors import DorisConnector, MySQLConnector
from backend.scheduler.manager import scheduler_manager

# 全局日志配置（需在获取任何 logger 之前执行）
LOG_LEVEL = settings.log.level.upper()
LOG_FORMAT = settings.log.format
DATE_FORMAT = settings.log.date_format
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
)

# 获取logger实例
logger = logging.getLogger("main")

app = FastAPI(title="Data Development Platform", version="1.0.0")

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router)

from backend.api.model.connector import ConnectorCreateReq, ConnectorUpdateReq

# 兼容性端点 - 映射旧API到新API结构
from backend.database.service.connector_service import ConnectorService
from backend.database.session import get_db_cursor

# 启动时创建数据库表
try:
    from backend.database.session import create_tables

    create_tables()
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to create database tables: {e}")
    import traceback

    logger.error(f"Traceback: {traceback.format_exc()}")


# 数据模型
class DatabaseConnection(BaseModel):
    name: str
    host: str
    port: int
    username: str
    password: str
    database: str
    db_type: str  # mysql 或 doris


class TableInfo(BaseModel):
    name: str
    columns: List[Dict[str, Any]]


class SQLQuery(BaseModel):
    sql: str
    params: Optional[Dict[str, Any]] = None


class QueryResult(BaseModel):
    data: List[Dict[str, Any]]
    total: int
    sql: str


# 数据库连接管理
class DatabaseManager:
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.logger = logging.getLogger("DatabaseManager")

    def add_connection(self, conn: DatabaseConnection) -> bool:
        try:
            self.logger.info(
                f"Adding database connection: {conn.name} ({conn.db_type})"
            )

            if conn.db_type == "mysql":
                connector = MySQLConnector(
                    host=conn.host,
                    port=conn.port,
                    username=conn.username,
                    password=conn.password,
                    database=conn.database,
                )
            elif conn.db_type == "doris":
                connector = DorisConnector(
                    host=conn.host,
                    port=conn.port,
                    username=conn.username,
                    password=conn.password,
                    database=conn.database,
                )
            else:
                error_msg = f"Unsupported database type: {conn.db_type}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

            # 测试连接
            if connector.test_connection():
                self.connections[conn.name] = connector
                self.logger.info(
                    f"Database connection '{conn.name}' added successfully"
                )
                return True
            else:
                error_msg = "Connection test failed"
                self.logger.error(f"Connection test failed for '{conn.name}'")
                raise Exception(error_msg)
        except Exception as e:
            self.logger.error(f"Failed to add connection '{conn.name}': {str(e)}")
            raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

    def get_connections(self) -> List[DatabaseConnection]:
        try:
            connections = [
                DatabaseConnection(
                    name=name,
                    host=conn.host,
                    port=conn.port,
                    username=conn.username,
                    password=conn.password,
                    database=conn.database,
                    db_type=conn.db_type,
                )
                for name, conn in self.connections.items()
            ]
            self.logger.info(f"Retrieved {len(connections)} database connections")
            return connections
        except Exception as e:
            self.logger.error(f"Failed to get connections: {str(e)}")
            raise

    def get_connection(self, name: str):
        conn = self.connections.get(name)
        if not conn:
            self.logger.warning(f"Connection '{name}' not found")
        return conn

    def remove_connection(self, name: str) -> bool:
        if name in self.connections:
            del self.connections[name]
            self.logger.info(f"Database connection '{name}' removed successfully")
            return True
        self.logger.warning(f"Attempted to remove non-existent connection '{name}'")
        return False

    def get_tables(self, conn_name: str) -> List[str]:
        conn = self.get_connection(conn_name)
        if not conn:
            error_msg = "Connection not found"
            self.logger.error(
                f"Failed to get tables: {error_msg} for connection '{conn_name}'"
            )
            raise HTTPException(status_code=404, detail=error_msg)

        try:
            tables = conn.get_tables()
            self.logger.info(
                f"Retrieved {len(tables)} tables from connection '{conn_name}'"
            )
            return tables
        except Exception as e:
            self.logger.error(
                f"Failed to get tables from connection '{conn_name}': {str(e)}"
            )
            raise HTTPException(
                status_code=500, detail=f"Failed to get tables: {str(e)}"
            )

    def get_table_structure(self, conn_name: str, table_name: str) -> TableInfo:
        conn = self.get_connection(conn_name)
        if not conn:
            error_msg = "Connection not found"
            self.logger.error(
                f"Failed to get table structure: {error_msg} for connection '{conn_name}'"
            )
            raise HTTPException(status_code=404, detail=error_msg)

        try:
            columns = conn.get_table_structure(table_name)
            self.logger.info(
                f"Retrieved table structure for '{table_name}' from connection '{conn_name}'"
            )
            return TableInfo(name=table_name, columns=columns)
        except Exception as e:
            self.logger.error(
                f"Failed to get table structure for '{table_name}' from connection '{conn_name}': {str(e)}"
            )
            raise HTTPException(
                status_code=500, detail=f"Failed to get table structure: {str(e)}"
            )

    def execute_query(self, conn_name: str, query: SQLQuery) -> QueryResult:
        conn = self.get_connection(conn_name)
        if not conn:
            error_msg = "Connection not found"
            self.logger.error(
                f"Failed to execute query: {error_msg} for connection '{conn_name}'"
            )
            raise HTTPException(status_code=404, detail=error_msg)

        try:
            self.logger.info(
                f"Executing query on connection '{conn_name}': {query.sql[:100]}..."
            )
            data = conn.execute_query(query.sql, query.params)
            self.logger.info(f"Query executed successfully, returned {len(data)} rows")
            return QueryResult(data=data, total=len(data), sql=query.sql)
        except Exception as e:
            self.logger.error(
                f"Failed to execute query on connection '{conn_name}': {str(e)}"
            )
            raise HTTPException(
                status_code=500, detail=f"Failed to execute query: {str(e)}"
            )

    def get_table_data(
        self, conn_name: str, table_name: str, limit: int = 100, offset: int = 0
    ) -> QueryResult:
        conn = self.get_connection(conn_name)
        if not conn:
            error_msg = "Connection not found"
            self.logger.error(
                f"Failed to get table data: {error_msg} for connection '{conn_name}'"
            )
            raise HTTPException(status_code=404, detail=error_msg)

        try:
            self.logger.info(
                f"Getting table data from '{table_name}' on connection '{conn_name}' (limit: {limit}, offset: {offset})"
            )
            data = conn.get_table_data(table_name, limit, offset)
            total = conn.get_table_count(table_name)
            self.logger.info(
                f"Retrieved {len(data)} rows from table '{table_name}' (total: {total})"
            )
            return QueryResult(
                data=data,
                total=total,
                sql=f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}",
            )
        except Exception as e:
            self.logger.error(
                f"Failed to get table data from '{table_name}' on connection '{conn_name}': {str(e)}"
            )
            raise HTTPException(
                status_code=500, detail=f"Failed to get table data: {str(e)}"
            )


# 全局数据库管理器
db_manager = DatabaseManager()


@app.get("/")
def read_root():
    logger.info("API: Root endpoint accessed")
    return {"message": "Data Development Platform API"}


@app.post("/api/connections")
def add_connection(connection: DatabaseConnection):
    """添加数据库连接 - 兼容性端点"""
    try:
        # 转换为新的API模型
        connector_req = ConnectorCreateReq(
            name=connection.name,
            db_type=connection.db_type,
            host=connection.host,
            port=connection.port,
            username=connection.username,
            password=connection.password,
            database=connection.database,
            description=f"Migrated from old API - {connection.db_type} connection",
            is_active=True,
        )

        # 使用新的服务
        cursor = next(get_db_cursor())
        service = ConnectorService(cursor)
        result = service.create_connector(connector_req.dict())

        logger.info(
            f"API: Database connection '{connection.name}' added successfully via compatibility endpoint"
        )
        return {"message": "Connection added successfully", "connection": result}
    except Exception as e:
        logger.error(
            f"API: Failed to add database connection via compatibility endpoint: {str(e)}"
        )
        raise


@app.on_event("startup")
def on_startup():
    try:
        # 创建数据库表
        logger.info("Starting database table creation...")
        from backend.database.session import create_tables

        create_tables()
        logger.info("Database tables created successfully")

        # 等待一下确保表创建完成
        import time

        time.sleep(1)

        # 启动调度器
        logger.info("Starting scheduler...")
        scheduler_manager.start()
        logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")


@app.get("/api/connections")
def get_connections():
    """获取所有数据库连接 - 兼容性端点"""
    try:
        # 使用新的服务
        cursor = next(get_db_cursor())
        service = ConnectorService(cursor)
        connectors = service.list_connectors(0, 1000)  # 获取所有连接器

        # 转换为旧API格式
        connections = []
        for conn in connectors:
            connections.append(
                DatabaseConnection(
                    name=conn.name,
                    host=conn.host,
                    port=conn.port,
                    username=conn.username,
                    password=conn.password,
                    database=conn.database_name,  # 使用 database_name 字段
                    db_type=conn.db_type,
                )
            )

        logger.info(
            f"API: Retrieved {len(connections)} database connections via compatibility endpoint"
        )
        return connections
    except Exception as e:
        logger.error(
            f"API: Failed to get database connections via compatibility endpoint: {str(e)}"
        )
        raise


@app.delete("/api/connections/{name}")
def remove_connection(name: str):
    """删除数据库连接 - 兼容性端点"""
    try:
        # 使用新的服务
        cursor = next(get_db_cursor())
        service = ConnectorService(cursor)

        # 先查找连接器ID
        connectors = service.list_connectors(0, 1000)
        connector_id = None
        for conn in connectors:
            if conn.name == name:
                connector_id = conn.id
                break

        if not connector_id:
            logger.warning(f"API: Connection '{name}' not found for deletion")
            raise HTTPException(status_code=404, detail="Connection not found")

        # 删除连接器
        success = service.delete_connector(connector_id)
        if success:
            logger.info(
                f"API: Database connection '{name}' removed successfully via compatibility endpoint"
            )
            return {"message": "Connection removed successfully"}
        else:
            logger.warning(f"API: Failed to delete connection '{name}'")
            raise HTTPException(status_code=500, detail="Failed to delete connection")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"API: Failed to remove database connection '{name}' via compatibility endpoint: {str(e)}"
        )
        raise


@app.get("/api/connections/{name}/tables")
def get_tables(name: str):
    """获取指定连接的所有表 - 兼容性端点"""
    try:
        # 使用新的服务
        cursor = next(get_db_cursor())
        service = ConnectorService(cursor)

        # 先查找连接器
        connectors = service.list_connectors(0, 1000)
        connector = None
        for conn in connectors:
            if conn.name == name:
                connector = conn
                break

        if not connector:
            logger.warning(f"API: Connection '{name}' not found for getting tables")
            raise HTTPException(status_code=404, detail="Connection not found")

        # 创建连接器实例并获取表
        if connector.db_type == "mysql":
            from backend.infra.connectors import MySQLConnector

            db_connector = MySQLConnector(
                host=connector.host,
                port=connector.port,
                username=connector.username,
                password=connector.password,
                database=connector.database_name,  # 使用 database_name 字段
            )
        elif connector.db_type == "doris":
            from backend.infra.connectors import DorisConnector

            db_connector = DorisConnector(
                host=connector.host,
                port=connector.port,
                username=connector.username,
                password=connector.password,
                database=connector.database_name,  # 使用 database_name 字段
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported database type: {connector.db_type}",
            )

        tables = db_connector.get_tables()
        logger.info(
            f"API: Retrieved {len(tables)} tables from connection '{name}' via compatibility endpoint"
        )
        return {"tables": tables}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"API: Failed to get tables from connection '{name}' via compatibility endpoint: {str(e)}"
        )
        raise


@app.get("/api/connections/{name}/tables/{table_name}/structure")
def get_table_structure(name: str, table_name: str):
    """获取指定表的结构 - 兼容性端点"""
    try:
        # 使用新的服务
        cursor = next(get_db_cursor())
        service = ConnectorService(cursor)

        # 先查找连接器
        connectors = service.list_connectors(0, 1000)
        connector = None
        for conn in connectors:
            if conn.name == name:
                connector = conn
                break

        if not connector:
            logger.warning(
                f"API: Connection '{name}' not found for getting table structure"
            )
            raise HTTPException(status_code=404, detail="Connection not found")

        # 创建连接器实例并获取表结构
        if connector.db_type == "mysql":
            from backend.infra.connectors import MySQLConnector

            db_connector = MySQLConnector(
                host=connector.host,
                port=connector.port,
                username=connector.username,
                password=connector.password,
                database=connector.database_name,  # 使用 database_name 字段
            )
        elif connector.db_type == "doris":
            from backend.infra.connectors import DorisConnector

            db_connector = DorisConnector(
                host=connector.host,
                port=connector.port,
                username=connector.username,
                password=connector.password,
                database=connector.database_name,  # 使用 database_name 字段
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported database type: {connector.db_type}",
            )

        columns = db_connector.get_table_structure(table_name)
        structure = TableInfo(name=table_name, columns=columns)

        logger.info(
            f"API: Retrieved table structure for '{table_name}' from connection '{name}' via compatibility endpoint"
        )
        return structure
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"API: Failed to get table structure for '{table_name}' from connection '{name}' via compatibility endpoint: {str(e)}"
        )
        raise


@app.post("/api/connections/{name}/query")
def execute_query(name: str, query: SQLQuery):
    """执行SQL查询 - 兼容性端点"""
    try:
        # 使用新的服务
        cursor = next(get_db_cursor())
        service = ConnectorService(cursor)

        # 先查找连接器
        connectors = service.list_connectors(0, 1000)
        connector = None
        for conn in connectors:
            if conn.name == name:
                connector = conn
                break

        if not connector:
            logger.warning(f"API: Connection '{name}' not found for executing query")
            raise HTTPException(status_code=404, detail="Connection not found")

        # 创建连接器实例并执行查询
        if connector.db_type == "mysql":
            from backend.infra.connectors import MySQLConnector

            db_connector = MySQLConnector(
                host=connector.host,
                port=connector.port,
                username=connector.username,
                password=connector.password,
                database=connector.database_name,  # 使用 database_name 字段
            )
        elif connector.db_type == "doris":
            from backend.infra.connectors import DorisConnector

            db_connector = DorisConnector(
                host=connector.host,
                port=connector.port,
                username=connector.username,
                password=connector.password,
                database=connector.database_name,  # 使用 database_name 字段
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported database type: {connector.db_type}",
            )

        data = db_connector.execute_query(query.sql, query.params)
        result = QueryResult(data=data, total=len(data), sql=query.sql)

        logger.info(
            f"API: Query executed successfully on connection '{name}' via compatibility endpoint"
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"API: Failed to execute query on connection '{name}' via compatibility endpoint: {str(e)}"
        )
        raise


@app.get("/api/connections/{name}/tables/{table_name}/data")
def get_table_data(name: str, table_name: str, limit: int = 100, offset: int = 0):
    """获取表数据 - 兼容性端点"""
    try:
        # 使用新的服务
        cursor = next(get_db_cursor())
        service = ConnectorService(cursor)

        # 先查找连接器
        connectors = service.list_connectors(0, 1000)
        connector = None
        for conn in connectors:
            if conn.name == name:
                connector = conn
                break

        if not connector:
            logger.warning(f"API: Connection '{name}' not found for getting table data")
            raise HTTPException(status_code=404, detail="Connection not found")

        # 创建连接器实例并获取表数据
        if connector.db_type == "mysql":
            from backend.infra.connectors import MySQLConnector

            db_connector = MySQLConnector(
                host=connector.host,
                port=connector.port,
                username=connector.username,
                password=connector.password,
                database=connector.database_name,  # 使用 database_name 字段
            )
        elif connector.db_type == "doris":
            from backend.infra.connectors import DorisConnector

            db_connector = DorisConnector(
                host=connector.host,
                port=connector.port,
                username=connector.username,
                password=connector.password,
                database=connector.database_name,  # 使用 database_name 字段
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported database type: {connector.db_type}",
            )

        data = db_connector.get_table_data(table_name, limit, offset)
        total = db_connector.get_table_count(table_name)
        result = QueryResult(
            data=data,
            total=total,
            sql=f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}",
        )

        logger.info(
            f"API: Retrieved table data from '{table_name}' on connection '{name}' via compatibility endpoint"
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"API: Failed to get table data from '{table_name}' on connection '{name}' via compatibility endpoint: {str(e)}"
        )
        raise


@app.get("/api/health")
def health_check():
    """健康检查"""
    logger.info("API: Health check requested")
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.app.host, port=settings.app.port)
