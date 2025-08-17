from fastapi import APIRouter, Depends, HTTPException, Body
from pymysql.cursors import DictCursor
from typing import Dict, Any, Optional
from backend.database.session import get_db_cursor
from backend.database.dao.chat import (
    ensure_tables as ensure_chat_tables,
    create_conversation as dao_create_conversation,
    get_conversation as dao_get_conversation,
    insert_message as dao_insert_message,
    list_messages_by_conversation as dao_list_messages_by_conversation,
    list_messages_for_response as dao_list_messages_for_response,
)
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


def ensure_tables():
    ensure_chat_tables()


@router.post("/conversations", response_model=ConversationRsp)
def create_conversation(cursor: DictCursor = Depends(get_db_cursor)):
    try:
        ensure_tables()
        conv_id = dao_create_conversation(cursor, None)
        row = dao_get_conversation(cursor, conv_id)
        return ConversationRsp(**row)
    except Exception as e:
        logger.exception(f"create_conversation error: {e}")
        raise HTTPException(status_code=500, detail=f"创建会话失败: {e}")


@router.get("/conversations/{conversation_id}", response_model=ConversationRsp)
def get_conversation(conversation_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    ensure_tables()
    row = dao_get_conversation(cursor, conversation_id)
    if not row:
        raise HTTPException(status_code=404, detail="会话不存在")
    return ConversationRsp(**row)


@router.get("/conversations/{conversation_id}/messages")
def list_messages(conversation_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    ensure_tables()
    rows = dao_list_messages_by_conversation(cursor, conversation_id)
    return rows


def _load_history(conversation_id: int, cursor: DictCursor):
    rows = dao_list_messages_by_conversation(cursor, conversation_id)
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


from typing import Optional, Dict as TypingDict


def _save_message(
    cursor: DictCursor,
    conversation_id: int,
    role: str,
    content: str,
    name: Optional[str] = None,
    tool_call: Optional[TypingDict[str, Any]] = None,
) -> int:
    return dao_insert_message(cursor, conversation_id, role, content, name, tool_call)


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
    conversation_id = req.conversation_id
    if not conversation_id:
        conversation_id = dao_create_conversation(cursor, None)

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
    rows = dao_list_messages_for_response(cursor, conversation_id)
    # 反序列化 tool_call
    for r in rows:
        if r.get("tool_call") and isinstance(r["tool_call"], (str, bytes)):
            try:
                r["tool_call"] = json.loads(r["tool_call"]) if r["tool_call"] else None
            except Exception:
                pass

    return ChatRsp(
        conversation_id=conversation_id,
        assistant_message=assistant_text,
        tool_call=tool_call_info,
        tool_result=tool_result,
        messages=rows,
    )
