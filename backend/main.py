from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os
import logging


from backend.infra.connectors import MySQLConnector, DorisConnector
from backend.api import api_router
from backend.scheduler.manager import scheduler_manager
from backend.database.session import create_tables

# 全局日志配置（需在获取任何 logger 之前执行）
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
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
    """添加数据库连接"""
    try:
        success = db_manager.add_connection(connection)
        logger.info(f"API: Database connection '{connection.name}' added successfully")
        return {"message": "Connection added successfully", "connection": connection}
    except Exception as e:
        logger.error(f"API: Failed to add database connection: {str(e)}")
        raise


@app.on_event("startup")
def on_startup():
    try:
        # 确保所有需要的表已创建
        create_tables()
        scheduler_manager.start()
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")


@app.get("/api/connections")
def get_connections():
    """获取所有数据库连接"""
    try:
        connections = db_manager.get_connections()
        logger.info(f"API: Retrieved {len(connections)} database connections")
        return connections
    except Exception as e:
        logger.error(f"API: Failed to get database connections: {str(e)}")
        raise


@app.delete("/api/connections/{name}")
def remove_connection(name: str):
    """删除数据库连接"""
    try:
        success = db_manager.remove_connection(name)
        if success:
            logger.info(f"API: Database connection '{name}' removed successfully")
            return {"message": "Connection removed successfully"}
        else:
            logger.warning(f"API: Attempted to remove non-existent connection '{name}'")
            raise HTTPException(status_code=404, detail="Connection not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to remove database connection '{name}': {str(e)}")
        raise


@app.get("/api/connections/{name}/tables")
def get_tables(name: str):
    """获取指定连接的所有表"""
    try:
        tables = db_manager.get_tables(name)
        logger.info(f"API: Retrieved {len(tables)} tables from connection '{name}'")
        return {"tables": tables}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to get tables from connection '{name}': {str(e)}")
        raise


@app.get("/api/connections/{name}/tables/{table_name}/structure")
def get_table_structure(name: str, table_name: str):
    """获取指定表的结构"""
    try:
        structure = db_manager.get_table_structure(name, table_name)
        logger.info(
            f"API: Retrieved table structure for '{table_name}' from connection '{name}'"
        )
        return structure
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"API: Failed to get table structure for '{table_name}' from connection '{name}': {str(e)}"
        )
        raise


@app.post("/api/connections/{name}/query")
def execute_query(name: str, query: SQLQuery):
    """执行SQL查询"""
    try:
        result = db_manager.execute_query(name, query)
        logger.info(f"API: Query executed successfully on connection '{name}'")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to execute query on connection '{name}': {str(e)}")
        raise


@app.get("/api/connections/{name}/tables/{table_name}/data")
def get_table_data(name: str, table_name: str, limit: int = 100, offset: int = 0):
    """获取表数据"""
    try:
        result = db_manager.get_table_data(name, table_name, limit, offset)
        logger.info(
            f"API: Retrieved table data from '{table_name}' on connection '{name}'"
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"API: Failed to get table data from '{table_name}' on connection '{name}': {str(e)}"
        )
        raise


@app.get("/api/health")
def health_check():
    """健康检查"""
    logger.info("API: Health check requested")
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
