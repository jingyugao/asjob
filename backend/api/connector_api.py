from fastapi import APIRouter, Depends, HTTPException, Query
from pymysql.cursors import DictCursor
from typing import List, Optional
from backend.database.session import get_db_cursor
from backend.database.service.connector_service import ConnectorService
from backend.api.model import (
    ConnectorCreateReq,
    ConnectorUpdateReq,
    ConnectorRsp,
    MessageRsp,
    TestConnectorRsp,
    StatsSummaryRsp,
    ParseConnectorReq,
    ParseConnectorRsp,
)
from backend.infra.llm.client import llm
from langchain.schema import SystemMessage, HumanMessage
import logging

router = APIRouter()
logger = logging.getLogger("connector_api")


@router.post("/", response_model=ConnectorRsp)
def create_connector(
    connector: ConnectorCreateReq, cursor: DictCursor = Depends(get_db_cursor)
):
    """创建连接器"""
    logger.info(f"Creating connector: {connector.name} ({connector.db_type})")
    service = ConnectorService(cursor)
    try:
        result = service.create_connector(connector.dict())
        logger.info(f"Connector '{connector.name}' created successfully")
        return result
    except ValueError as e:
        logger.warning(f"Failed to create connector '{connector.name}': {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create connector '{connector.name}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.get("/{connector_id}", response_model=ConnectorRsp)
def get_connector(connector_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    """获取连接器"""
    logger.info(f"Getting connector with ID: {connector_id}")
    service = ConnectorService(cursor)
    try:
        connector = service.get_connector(connector_id)
        if not connector:
            logger.warning(f"Connector with ID {connector_id} not found")
            raise HTTPException(status_code=404, detail="连接器不存在")
        logger.info(f"Retrieved connector '{connector.name}' successfully")
        return connector
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get connector with ID {connector_id}: {str(e)}")
        raise


@router.get("/", response_model=List[ConnectorRsp])
def list_connectors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db_type: Optional[str] = Query(None),
    active_only: bool = Query(False),
    cursor: DictCursor = Depends(get_db_cursor),
):
    """列出连接器"""
    logger.info(
        f"Listing connectors (skip: {skip}, limit: {limit}, db_type: {db_type}, active_only: {active_only})"
    )
    service = ConnectorService(cursor)

    try:
        if active_only:
            result = service.list_active_connectors()
            logger.info(f"Retrieved {len(result)} active connectors")
        elif db_type:
            result = service.list_connectors_by_type(db_type)
            logger.info(f"Retrieved {len(result)} connectors of type '{db_type}'")
        else:
            result = service.list_connectors(skip, limit)
            logger.info(f"Retrieved {len(result)} connectors")
        return result
    except Exception as e:
        logger.error(f"Failed to list connectors: {str(e)}")
        raise


@router.put("/{connector_id}", response_model=ConnectorRsp)
def update_connector(
    connector_id: int,
    connector: ConnectorUpdateReq,
    cursor: DictCursor = Depends(get_db_cursor),
):
    """更新连接器"""
    logger.info(f"Updating connector with ID: {connector_id}")
    service = ConnectorService(cursor)
    try:
        updated = service.update_connector(
            connector_id, connector.dict(exclude_unset=True)
        )
        if not updated:
            logger.warning(f"Connector with ID {connector_id} not found for update")
            raise HTTPException(status_code=404, detail="连接器不存在")
        logger.info(f"Connector '{updated.name}' updated successfully")
        return updated
    except ValueError as e:
        logger.warning(f"Failed to update connector {connector_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update connector {connector_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/{connector_id}", response_model=MessageRsp)
def delete_connector(connector_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    """删除连接器"""
    logger.info(f"Deleting connector with ID: {connector_id}")
    service = ConnectorService(cursor)
    try:
        if not service.delete_connector(connector_id):
            logger.warning(f"Connector with ID {connector_id} not found for deletion")
            raise HTTPException(status_code=404, detail="连接器不存在")
        logger.info(f"Connector with ID {connector_id} deleted successfully")
        return MessageRsp(message="删除成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete connector {connector_id}: {str(e)}")
        raise


@router.post("/{connector_id}/activate", response_model=MessageRsp)
def activate_connector(connector_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    """激活连接器"""
    logger.info(f"Activating connector with ID: {connector_id}")
    service = ConnectorService(cursor)
    try:
        if not service.activate_connector(connector_id):
            logger.warning(f"Connector with ID {connector_id} not found for activation")
            raise HTTPException(status_code=404, detail="连接器不存在")
        logger.info(f"Connector with ID {connector_id} activated successfully")
        return MessageRsp(message="激活成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to activate connector {connector_id}: {str(e)}")
        raise


@router.post("/{connector_id}/deactivate", response_model=MessageRsp)
def deactivate_connector(
    connector_id: int, cursor: DictCursor = Depends(get_db_cursor)
):
    """停用连接器"""
    logger.info(f"Deactivating connector with ID: {connector_id}")
    service = ConnectorService(cursor)
    try:
        if not service.deactivate_connector(connector_id):
            logger.warning(
                f"Connector with ID {connector_id} not found for deactivation"
            )
            raise HTTPException(status_code=404, detail="连接器不存在")
        logger.info(f"Connector with ID {connector_id} deactivated successfully")
        return MessageRsp(message="停用成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deactivate connector {connector_id}: {str(e)}")
        raise


@router.post("/{connector_id}/test", response_model=TestConnectorRsp)
def test_connector(connector_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    """测试连接器连接"""
    logger.info(f"Testing connector with ID: {connector_id}")
    service = ConnectorService(cursor)
    try:
        if not service.get_connector(connector_id):
            logger.warning(f"Connector with ID {connector_id} not found for testing")
            raise HTTPException(status_code=404, detail="连接器不存在")

        is_connected = service.test_connector(connector_id)
        logger.info(
            f"Connector {connector_id} test result: {'connected' if is_connected else 'disconnected'}"
        )
        return TestConnectorRsp(connected=is_connected)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test connector {connector_id}: {str(e)}")
        raise


@router.get("/stats/summary", response_model=StatsSummaryRsp)
def get_connector_stats(cursor: DictCursor = Depends(get_db_cursor)):
    """获取连接器统计信息"""
    logger.info("Getting connector statistics")
    service = ConnectorService(cursor)
    try:
        stats = service.get_connector_stats()
        logger.info(f"Retrieved connector stats: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Failed to get connector stats: {str(e)}")
        raise


@router.get("/search/{keyword}", response_model=List[ConnectorRsp])
def search_connectors(keyword: str, cursor: DictCursor = Depends(get_db_cursor)):
    """搜索连接器"""
    logger.info(f"Searching connectors with keyword: {keyword}")
    service = ConnectorService(cursor)
    try:
        results = service.search_connectors(keyword)
        logger.info(f"Found {len(results)} connectors matching keyword '{keyword}'")
        return results
    except Exception as e:
        logger.error(f"Failed to search connectors with keyword '{keyword}': {str(e)}")
        raise


@router.post("/parse", response_model=ParseConnectorRsp)
def parse_connector(req: ParseConnectorReq):
    """使用 LLM 解析任意文本中的连接信息"""
    try:
        system_prompt = (
            "你是一个严格的解析器。\n"
            "从用户提供的文本中提取数据库连接信息，仅返回JSON，不要解释。\n"
            "字段: db_type(host的数据库类型, 只能是mysql或doris), host, port(数字), username, password, database。\n"
            "若缺失字段，请合理推断常见默认值: port: mysql=3306, doris=9030; database 可用 chatjob。\n"
            "确保返回是一个严格的 JSON 对象，不包含多余文本。"
        )
        user_prompt = "文本如下，提取连接信息并返回JSON: \n\n" + req.text
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        resp = llm.invoke(messages)
        content = resp.content if hasattr(resp, "content") else str(resp)

        import json

        try:
            data = json.loads(content)
        except Exception:
            # 容错：尝试截取第一个大括号 JSON 片段
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                data = json.loads(content[start : end + 1])
            else:
                raise ValueError("解析失败: 模型未返回有效JSON")

        # 归一化和默认值
        db_type = str(data.get("db_type", "mysql")).lower()
        if db_type not in ("mysql", "doris"):
            db_type = "mysql"
        host = data.get("host") or "localhost"
        port = int(data.get("port") or (9030 if db_type == "doris" else 3306))
        username = data.get("username") or "root"
        password = data.get("password") or ""
        database = data.get("database") or "chatjob"

        return ParseConnectorRsp(
            db_type=db_type,
            host=str(host),
            port=port,
            username=str(username),
            password=str(password),
            database=str(database),
        )
    except Exception as e:
        logger.error(f"Failed to parse connector from text: {str(e)}")
        raise HTTPException(status_code=400, detail=f"解析失败: {str(e)}")
