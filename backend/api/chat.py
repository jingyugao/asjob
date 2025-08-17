from fastapi import APIRouter, Depends, HTTPException, Body
from pymysql.cursors import DictCursor
from typing import Dict, Any, Optional
from datetime import datetime
from backend.database.session import get_db_cursor, create_tables, db_connection
from backend.database.model.chat import ConversationModel, MessageModel
from backend.database.dao.chat_dao import ChatDAO
from backend.api.model.chat import (
    ChatReq,
    ChatRsp,
    ConversationRsp,
    ConversationCreateReq,
    MessageRsp,
)
from backend.infra.llm.client import llm
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import json
import logging


router = APIRouter()
logger = logging.getLogger("chat_api")


# 简单工具注册表示例
def list_tools() -> Dict[str, Any]:
    return {
        "echo": {
            "schema": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
            "fn": lambda args: {"echo": args.get("text", "")},
            "description": "回显输入文本",
        }
    }


def convert_conversation_to_response(db_model: Dict[str, Any]) -> ConversationRsp:
    """将数据库记录转换为API响应模型"""
    # 转换datetime到字符串
    if db_model.get('created_at') and isinstance(db_model['created_at'], datetime):
        db_model['created_at'] = db_model['created_at'].isoformat()
    if db_model.get('updated_at') and isinstance(db_model['updated_at'], datetime):
        db_model['updated_at'] = db_model['updated_at'].isoformat()
    
    return ConversationRsp(**db_model)


def convert_message_to_response(db_model: Dict[str, Any]) -> MessageRsp:
    """将消息数据库记录转换为API响应模型"""
    # 转换datetime到字符串
    if db_model.get('created_at') and isinstance(db_model['created_at'], datetime):
        db_model['created_at'] = db_model['created_at'].isoformat()
    
    return MessageRsp(**db_model)


def ensure_tables(cursor: DictCursor = None):
    # 复用现有入口，追加聊天表
    create_tables()
    with db_connection.get_cursor() as cursor:
        dao = ChatDAO(cursor)
        dao.ensure_tables()


@router.post("/conversations", response_model=ConversationRsp)
def create_conversation(cursor: DictCursor = Depends(get_db_cursor)):
    try:
        ensure_tables()
        dao = ChatDAO(cursor)
        row = dao.create_conversation(title=None)
        return convert_conversation_to_response(row)
    except Exception as e:
        logger.exception(f"create_conversation error: {e}")
        raise HTTPException(status_code=500, detail=f"创建会话失败: {e}")


@router.get("/conversations/{conversation_id}", response_model=ConversationRsp)
def get_conversation(conversation_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    ensure_tables()
    dao = ChatDAO(cursor)
    row = dao.get_conversation(conversation_id)
    if not row:
        raise HTTPException(status_code=404, detail="会话不存在")
    return convert_conversation_to_response(row)


@router.get("/conversations/{conversation_id}/messages")
def list_messages(conversation_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    ensure_tables()
    dao = ChatDAO(cursor)
    rows = dao.list_messages(conversation_id)
    return rows


def _load_history(conversation_id: int, cursor: DictCursor):
    dao = ChatDAO(cursor)
    history = dao.load_history(conversation_id)
    messages = []
    for role, content, name in history:
        if role == "system":
            messages.append(SystemMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        elif role == "tool":
            # 将工具结果作为系统信息供模型参考
            messages.append(
                SystemMessage(content=f"TOOL_RESULT[{name}] => {content}")
            )
        else:
            messages.append(HumanMessage(content=content))
    return messages


from typing import Optional, Dict as TypingDict


def _save_message(
    cursor: DictCursor,
    conversation_id: int,
    role: str,
    content: str,
    name: Optional[str] = None,
    tool_call: Optional[TypingDict[str, Any]] = None,
) -> int:
    dao = ChatDAO(cursor)
    return dao.insert_message(conversation_id, role, content, name, tool_call)


@router.post("/tools")
def get_tools():
    # 提供前端展示的工具列表
    registry = list_tools()
    tools = [
        {
            "name": name,
            "schema": meta.get("schema"),
            "description": meta.get("description"),
        }
        for name, meta in registry.items()
    ]
    return {"tools": tools}


@router.post("/ask", response_model=ChatRsp)
def chat(req: ChatReq, cursor: DictCursor = Depends(get_db_cursor)):
    ensure_tables()
    dao = ChatDAO(cursor)
    
    conversation_id = req.conversation_id
    if not conversation_id:
        row = dao.create_conversation(title=None)
        conversation_id = row['id']

    # 保存用户消息
    _save_message(cursor, conversation_id, "user", req.content)

    # 加载历史
    history = _load_history(conversation_id, cursor)
    # 注入工具调用说明
    tool_instruction = (
        '你可以在需要外部工具时，仅返回一个 JSON 对象，格式为 {"tool":"工具名","arguments":{...}}，'
        "不要添加其他文本；若不需要工具，则直接自然语言回答。可用工具请根据后端提供的 /tools 列表自行选择。"
    )
    history.insert(0, SystemMessage(content=tool_instruction))

    # 基础回答
    response = llm.invoke(history)
    assistant_text = response.content if hasattr(response, "content") else str(response)
    tool_call_info = None
    tool_result = None

    # 简单函数调用检测：如果模型以JSON形式提出调用
    try:
        maybe_json = assistant_text.strip()
        if maybe_json.startswith("{") and maybe_json.endswith("}"):
            call = json.loads(maybe_json)
            if isinstance(call, dict) and "tool" in call and "arguments" in call:
                registry = list_tools()
                tool_name = call["tool"]
                if tool_name in registry:
                    tool_call_info = {"name": tool_name, "arguments": call["arguments"]}
                    tool_fn = registry[tool_name]["fn"]
                    tool_result = tool_fn(call["arguments"])  # 执行
                    # 把工具调用和结果作为消息写入历史
                    _save_message(
                        cursor,
                        conversation_id,
                        "assistant",
                        assistant_text,
                        name=tool_name,
                        tool_call=tool_call_info,
                    )
                    _save_message(
                        cursor,
                        conversation_id,
                        "tool",
                        json.dumps(tool_result),
                        name=tool_name,
                    )
                    # 二次让模型基于工具结果回复
                    history2 = _load_history(conversation_id, cursor)
                    response2 = llm.invoke(history2)
                    assistant_text = (
                        response2.content
                        if hasattr(response2, "content")
                        else str(response2)
                    )
    except Exception as e:
        logger.warning(f"tool call 解析/执行失败: {e}")

    # 保存最终助手消息
    _save_message(cursor, conversation_id, "assistant", assistant_text)

    # 返回完整消息列表
    rows = dao.get_messages_after_id(conversation_id, 0)
    
    return ChatRsp(
        conversation_id=conversation_id,
        messages=rows,
        assistant_message=assistant_text,
        tool_call=tool_call_info,
        tool_result=tool_result,
    )
