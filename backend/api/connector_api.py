from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database.session import get_db_session
from ..database.service.connector_service import ConnectorService
from ..database.schema.connector_schema import (
    ConnectorCreate,
    ConnectorUpdate,
    ConnectorResponse,
)

router = APIRouter()


@router.post("/", response_model=ConnectorResponse)
def create_connector(
    connector: ConnectorCreate, session: Session = Depends(get_db_session)
):
    """创建连接器"""
    service = ConnectorService(session)
    try:
        return service.create_connector(connector.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.get("/{connector_id}", response_model=ConnectorResponse)
def get_connector(connector_id: int, session: Session = Depends(get_db_session)):
    """获取连接器"""
    service = ConnectorService(session)
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
    session: Session = Depends(get_db_session),
):
    """列出连接器"""
    service = ConnectorService(session)

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
    session: Session = Depends(get_db_session),
):
    """更新连接器"""
    service = ConnectorService(session)
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
def delete_connector(connector_id: int, session: Session = Depends(get_db_session)):
    """删除连接器"""
    service = ConnectorService(session)
    if not service.delete_connector(connector_id):
        raise HTTPException(status_code=404, detail="连接器不存在")
    return {"message": "删除成功"}


@router.post("/{connector_id}/activate")
def activate_connector(connector_id: int, session: Session = Depends(get_db_session)):
    """激活连接器"""
    service = ConnectorService(session)
    if not service.activate_connector(connector_id):
        raise HTTPException(status_code=404, detail="连接器不存在")
    return {"message": "激活成功"}


@router.post("/{connector_id}/deactivate")
def deactivate_connector(connector_id: int, session: Session = Depends(get_db_session)):
    """停用连接器"""
    service = ConnectorService(session)
    if not service.deactivate_connector(connector_id):
        raise HTTPException(status_code=404, detail="连接器不存在")
    return {"message": "停用成功"}


@router.post("/{connector_id}/test")
def test_connector(connector_id: int, session: Session = Depends(get_db_session)):
    """测试连接器连接"""
    service = ConnectorService(session)
    if not service.get_connector(connector_id):
        raise HTTPException(status_code=404, detail="连接器不存在")

    is_connected = service.test_connector(connector_id)
    return {"connected": is_connected}


@router.get("/stats/summary")
def get_connector_stats(session: Session = Depends(get_db_session)):
    """获取连接器统计信息"""
    service = ConnectorService(session)
    return service.get_connector_stats()


@router.get("/search/{keyword}", response_model=List[ConnectorResponse])
def search_connectors(keyword: str, session: Session = Depends(get_db_session)):
    """搜索连接器"""
    service = ConnectorService(session)
    return service.search_connectors(keyword)
