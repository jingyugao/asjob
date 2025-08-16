from fastapi import APIRouter, Depends, HTTPException, Query
from pymysql.cursors import DictCursor
from typing import List
from backend.database.session import get_db_cursor
from backend.database.service.knowledge_service import KnowledgeService
from backend.api.model.knowledge import (
    KnowledgeCreateReq,
    KnowledgeUpdateReq,
    KnowledgeRsp,
    KnowledgeListRsp,
)
import logging


router = APIRouter()
logger = logging.getLogger("knowledge_api")


@router.post("/", response_model=KnowledgeRsp)
def create_knowledge(
    body: KnowledgeCreateReq, cursor: DictCursor = Depends(get_db_cursor)
):
    service = KnowledgeService(cursor)
    try:
        created = service.create_knowledge(body.dict())
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.get("/by-target", response_model=KnowledgeListRsp)
def list_by_target(
    target_type: str = Query(..., description="database|table|field"),
    target_name: str = Query(..., description="connector::db::table::field"),
    cursor: DictCursor = Depends(get_db_cursor),
):
    service = KnowledgeService(cursor)
    try:
        items = service.list_for_target(target_type, target_name)
        return {"items": items}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/by-prefix", response_model=KnowledgeListRsp)
def list_by_prefix(
    target_type: str = Query(..., description="database|table|field"),
    target_prefix: str = Query(
        ..., description="如 connector::db 或 connector::db::table"
    ),
    cursor: DictCursor = Depends(get_db_cursor),
):
    service = KnowledgeService(cursor)
    items = service.list_by_prefix(target_type, target_prefix)
    return {"items": items}


@router.put("/{knowledge_id}", response_model=KnowledgeRsp)
def update_knowledge(
    knowledge_id: int,
    body: KnowledgeUpdateReq,
    cursor: DictCursor = Depends(get_db_cursor),
):
    service = KnowledgeService(cursor)
    updated = service.update_content(knowledge_id, body.content)
    if not updated:
        raise HTTPException(status_code=404, detail="知识不存在")
    return updated


@router.delete("/{knowledge_id}")
def delete_knowledge(knowledge_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    service = KnowledgeService(cursor)
    ok = service.delete(knowledge_id)
    if not ok:
        raise HTTPException(status_code=404, detail="知识不存在")
    return {"message": "删除成功"}
