from fastapi import APIRouter, Depends, HTTPException, Query
from pymysql.cursors import DictCursor
from typing import List, Optional
from backend.database.session import get_db_cursor
from backend.database.service.connector_service import ConnectorService
from backend.database.schema.connector_schema import (
    ConnectorCreate,
    ConnectorUpdate,
    ConnectorResponse,
)

router = APIRouter()


@router.post("/", response_model=ConnectorResponse)
def create_connector(
    connector: ConnectorCreate, cursor: DictCursor = Depends(get_db_cursor)
):
    """创建连接器"""
    service = ConnectorService(cursor)
    try:
        return service.create_connector(connector.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.get("/{connector_id}", response_model=ConnectorResponse)
def get_connector(connector_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    """获取连接器"""
    service = ConnectorService(cursor)
    connector = service.get_connector(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="连接器不存在")
    return connector


@router.get("/", response_model=List[ConnectorResponse])
def list_connectors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db_type: Optional[str] = Query(None),
    active_only: bool = Query(False),
    cursor: DictCursor = Depends(get_db_cursor),
):
    """列出连接器"""
    service = ConnectorService(cursor)

    if active_only:
        return service.list_active_connectors()
    elif db_type:
        return service.list_connectors_by_type(db_type)
    else:
        return service.list_connectors(skip, limit)


@router.put("/{connector_id}", response_model=ConnectorResponse)
def update_connector(
    connector_id: int,
    connector: ConnectorUpdate,
    cursor: DictCursor = Depends(get_db_cursor),
):
    """更新连接器"""
    service = ConnectorService(cursor)
    try:
        updated = service.update_connector(
            connector_id, connector.dict(exclude_unset=True)
        )
        if not updated:
            raise HTTPException(status_code=404, detail="连接器不存在")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/{connector_id}")
def delete_connector(connector_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    """删除连接器"""
    service = ConnectorService(cursor)
    if not service.delete_connector(connector_id):
        raise HTTPException(status_code=404, detail="连接器不存在")
    return {"message": "删除成功"}


@router.post("/{connector_id}/activate")
def activate_connector(connector_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    """激活连接器"""
    service = ConnectorService(cursor)
    if not service.activate_connector(connector_id):
        raise HTTPException(status_code=404, detail="连接器不存在")
    return {"message": "激活成功"}


@router.post("/{connector_id}/deactivate")
def deactivate_connector(connector_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    """停用连接器"""
    service = ConnectorService(cursor)
    if not service.deactivate_connector(connector_id):
        raise HTTPException(status_code=404, detail="连接器不存在")
    return {"message": "停用成功"}


@router.post("/{connector_id}/test")
def test_connector(connector_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    """测试连接器连接"""
    service = ConnectorService(cursor)
    if not service.get_connector(connector_id):
        raise HTTPException(status_code=404, detail="连接器不存在")

    is_connected = service.test_connector(connector_id)
    return {"connected": is_connected}


@router.get("/stats/summary")
def get_connector_stats(cursor: DictCursor = Depends(get_db_cursor)):
    """获取连接器统计信息"""
    service = ConnectorService(cursor)
    return service.get_connector_stats()


@router.get("/search/{keyword}", response_model=List[ConnectorResponse])
def search_connectors(keyword: str, cursor: DictCursor = Depends(get_db_cursor)):
    """搜索连接器"""
    service = ConnectorService(cursor)
    return service.search_connectors(keyword)
