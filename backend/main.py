from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os


from backend.connectors import MySQLConnector, DorisConnector
from backend.api import api_router
from backend.database.init_db import init_database

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

    def add_connection(self, conn: DatabaseConnection) -> bool:
        try:
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
                raise ValueError(f"Unsupported database type: {conn.db_type}")

            # 测试连接
            if connector.test_connection():
                self.connections[conn.name] = connector
                return True
            else:
                raise Exception("Connection test failed")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

    def get_connections(self) -> List[DatabaseConnection]:
        return [
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

    def get_connection(self, name: str):
        return self.connections.get(name)

    def remove_connection(self, name: str) -> bool:
        if name in self.connections:
            del self.connections[name]
            return True
        return False

    def get_tables(self, conn_name: str) -> List[str]:
        conn = self.get_connection(conn_name)
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found")

        try:
            return conn.get_tables()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get tables: {str(e)}"
            )

    def get_table_structure(self, conn_name: str, table_name: str) -> TableInfo:
        conn = self.get_connection(conn_name)
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found")

        try:
            columns = conn.get_table_structure(table_name)
            return TableInfo(name=table_name, columns=columns)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get table structure: {str(e)}"
            )

    def execute_query(self, conn_name: str, query: SQLQuery) -> QueryResult:
        conn = self.get_connection(conn_name)
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found")

        try:
            data = conn.execute_query(query.sql, query.params)
            return QueryResult(data=data, total=len(data), sql=query.sql)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to execute query: {str(e)}"
            )

    def get_table_data(
        self, conn_name: str, table_name: str, limit: int = 100, offset: int = 0
    ) -> QueryResult:
        conn = self.get_connection(conn_name)
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found")

        try:
            data = conn.get_table_data(table_name, limit, offset)
            total = conn.get_table_count(table_name)
            return QueryResult(
                data=data,
                total=total,
                sql=f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get table data: {str(e)}"
            )


# 全局数据库管理器
db_manager = DatabaseManager()


@app.get("/")
def read_root():
    return {"message": "Data Development Platform API"}


@app.post("/api/connections")
def add_connection(connection: DatabaseConnection):
    """添加数据库连接"""
    success = db_manager.add_connection(connection)
    return {"message": "Connection added successfully", "connection": connection}


@app.get("/api/connections")
def get_connections():
    """获取所有数据库连接"""
    return db_manager.get_connections()


@app.delete("/api/connections/{name}")
def remove_connection(name: str):
    """删除数据库连接"""
    success = db_manager.remove_connection(name)
    if success:
        return {"message": "Connection removed successfully"}
    else:
        raise HTTPException(status_code=404, detail="Connection not found")


@app.get("/api/connections/{name}/tables")
def get_tables(name: str):
    """获取指定连接的所有表"""
    tables = db_manager.get_tables(name)
    return {"tables": tables}


@app.get("/api/connections/{name}/tables/{table_name}/structure")
def get_table_structure(name: str, table_name: str):
    """获取指定表的结构"""
    structure = db_manager.get_table_structure(name, table_name)
    return structure


@app.post("/api/connections/{name}/query")
def execute_query(name: str, query: SQLQuery):
    """执行SQL查询"""
    result = db_manager.execute_query(name, query)
    return result


@app.get("/api/connections/{name}/tables/{table_name}/data")
def get_table_data(name: str, table_name: str, limit: int = 100, offset: int = 0):
    """获取表数据"""
    result = db_manager.get_table_data(name, table_name, limit, offset)
    return result


@app.get("/api/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
