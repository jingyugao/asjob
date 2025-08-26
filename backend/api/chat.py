import json
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from pymysql.cursors import DictCursor

from backend.api.model.chat import (
    ChatReq,
    ChatRsp,
    ConversationCreateReq,
    ConversationRsp,
    MessageRsp,
)
from backend.database.dao.chat_dao import ChatDAO
from backend.database.session import create_tables, db_connection, get_db_cursor
from backend.infra.llm.client import llm

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


@router.post("/conversations", response_model=ConversationRsp)
def create_conversation(cursor: DictCursor = Depends(get_db_cursor)):
    try:
        chat_dao = ChatDAO(cursor)
        chat_dao.ensure_tables()
        conversation = chat_dao.create_conversation()
        return ConversationRsp(**conversation.dict())
    except Exception as e:
        logger.exception(f"create_conversation error: {e}")
        raise HTTPException(status_code=500, detail=f"创建会话失败: {e}")


@router.get("/conversations/{conversation_id}", response_model=ConversationRsp)
def get_conversation(conversation_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    chat_dao = ChatDAO(cursor)
    chat_dao.ensure_tables()
    conversation = chat_dao.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    return ConversationRsp(**conversation.dict())


@router.get("/conversations/{conversation_id}/messages")
def list_messages(conversation_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    chat_dao = ChatDAO(cursor)
    chat_dao.ensure_tables()
    return chat_dao.list_messages(conversation_id)


def _load_history(conversation_id: int, chat_dao: ChatDAO):
    rows = chat_dao.get_message_history(conversation_id)
    lc_messages = []
    for r in rows:
        role = r["role"]
        content = r["content"]
        if role == "system":
            lc_messages.append(SystemMessage(content=content))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=content))
        elif role == "tool":
            # 将工具结果作为系统信息供模型参考
            lc_messages.append(
                SystemMessage(content=f"TOOL_RESULT[{r.get('name')}] => {content}")
            )
        else:
            lc_messages.append(HumanMessage(content=content))
    return lc_messages


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
    chat_dao = ChatDAO(cursor)
    chat_dao.ensure_tables()

    conversation_id = req.conversation_id
    if not conversation_id:
        conversation = chat_dao.create_conversation()
        conversation_id = conversation.id

    # 保存用户消息
    chat_dao.save_message(conversation_id, "user", req.content)

    # 加载历史
    history = _load_history(conversation_id, chat_dao)
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
                    chat_dao.save_message(
                        conversation_id,
                        "assistant",
                        assistant_text,
                        name=tool_name,
                        tool_call=tool_call_info,
                    )
                    chat_dao.save_message(
                        conversation_id,
                        "tool",
                        json.dumps(tool_result),
                        name=tool_name,
                    )
                    # 二次让模型基于工具结果回复
                    history2 = _load_history(conversation_id, chat_dao)
                    response2 = llm.invoke(history2)
                    assistant_text = (
                        response2.content
                        if hasattr(response2, "content")
                        else str(response2)
                    )
    except Exception as e:
        logger.warning(f"tool call 解析/执行失败: {e}")

    # 保存最终助手消息
    chat_dao.save_message(conversation_id, "assistant", assistant_text)

    # 返回完整消息列表
    messages = chat_dao.list_messages(conversation_id)

    return ChatRsp(
        conversation_id=conversation_id,
        assistant_message=assistant_text,
        tool_call=tool_call_info,
        tool_result=tool_result,
        messages=messages,
    )
